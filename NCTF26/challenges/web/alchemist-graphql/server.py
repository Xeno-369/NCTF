#!/usr/bin/env python3
"""
Alchemist GraphQL Engine v4.2
High-performance AST Query Cache & Microservice Auth Hub.
Exposes a GraphQL API at /graphql with custom AST normalization and JWS verification.
"""

import base64
import hashlib
import hmac
import json
import os
import re
import socket
import sys
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("PORT", "18083"))
FLAG = os.environ.get("FLAG", "NCTF{REDACTED}")
DECOY_FLAG = "NCTF{graphql_introspection_honey_field}"
D_HINT_MASK = os.environ.get("D_HINT_MASK", "1111111111111111111111111111111111111111111111111111111111111111")

REDUCED_PRIME = 65521  # 0xFFF1 curve twist modulus

INTERNAL_CONFIG = {
    "kid": "alchemist-master-2026",
    "crv": "P-256",
    "x": "0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296",
    "y": "0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5",
    "d_hint_mask": D_HINT_MASK,
}

# --- GraphQL Lexer & Parser ---

TOKEN_SPEC = [
    ("STRING", r'\"(?:[^\"\\]|\\.)*\"'),
    ("ELLIPSIS", r"\.\.\."),
    ("NAME", r"[A-Za-z_][A-Za-z0-9_]*"),
    ("NUMBER", r"-?[0-9]+(?:\.[0-9]+)?"),
    ("PUNCT", r"[\{\}\(\):,=@!]"),
    ("WS", r"[\s,]+"),
]
TOK_REGEX = re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC))


def tokenize(text: str):
    tokens = []
    for mo in TOK_REGEX.finditer(text):
        kind = mo.lastgroup
        if kind == "WS":
            continue
        val = mo.group()
        if kind == "STRING":
            val = val[1:-1].encode().decode("unicode_escape")
        tokens.append((kind, val))
    tokens.append(("EOF", ""))
    return tokens


class Field:
    def __init__(self, alias, name, arguments, directives, selection_set):
        self.alias = alias
        self.name = name
        self.arguments = arguments or {}
        self.directives = directives or []
        self.selection_set = selection_set or []


class FragmentSpread:
    def __init__(self, name, directives):
        self.name = name
        self.directives = directives or []


class FragmentDef:
    def __init__(self, name, on_type, selection_set):
        self.name = name
        self.on_type = on_type
        self.selection_set = selection_set


class OperationDef:
    def __init__(self, op_type, name, selection_set):
        self.op_type = op_type
        self.name = name
        self.selection_set = selection_set


class GraphQLParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def consume(self, expected_kind=None, expected_val=None):
        kind, val = self.tokens[self.pos]
        if expected_kind and kind != expected_kind:
            raise ValueError(f"Expected token {expected_kind}, got {kind} ({val})")
        if expected_val and val != expected_val:
            raise ValueError(f"Expected value {expected_val}, got {val}")
        self.pos += 1
        return val

    def parse_document(self):
        defs = []
        while self.peek()[0] != "EOF":
            _, val = self.peek()
            if val in ("query", "mutation"):
                op_type = self.consume()
                name = None
                if self.peek()[0] == "NAME":
                    name = self.consume()
                sel_set = self.parse_selection_set()
                defs.append(OperationDef(op_type, name, sel_set))
            elif val == "{":
                sel_set = self.parse_selection_set()
                defs.append(OperationDef("query", None, sel_set))
            elif val == "fragment":
                self.consume()
                frag_name = self.consume("NAME")
                self.consume("NAME", "on")
                on_type = self.consume("NAME")
                sel_set = self.parse_selection_set()
                defs.append(FragmentDef(frag_name, on_type, sel_set))
            else:
                raise ValueError(f"Unexpected token in document: {val}")
        return defs

    def parse_selection_set(self):
        self.consume("PUNCT", "{")
        selections = []
        while self.peek()[1] != "}":
            if self.peek()[0] == "ELLIPSIS":
                self.consume()
                name = self.consume("NAME")
                dirs = self.parse_directives()
                selections.append(FragmentSpread(name, dirs))
            else:
                selections.append(self.parse_field())
        self.consume("PUNCT", "}")
        return selections

    def parse_field(self):
        alias = None
        name = self.consume("NAME")
        if self.peek()[1] == ":":
            self.consume("PUNCT", ":")
            alias = name
            name = self.consume("NAME")

        args = {}
        if self.peek()[1] == "(":
            self.consume("PUNCT", "(")
            while self.peek()[1] != ")":
                arg_name = self.consume("NAME")
                self.consume("PUNCT", ":")
                arg_val = self.parse_value()
                args[arg_name] = arg_val
            self.consume("PUNCT", ")")

        dirs = self.parse_directives()
        sub_sel = []
        if self.peek()[1] == "{":
            sub_sel = self.parse_selection_set()

        return Field(alias, name, args, dirs, sub_sel)

    def parse_directives(self):
        dirs = []
        while self.peek()[1] == "@":
            self.consume("PUNCT", "@")
            dname = self.consume("NAME")
            dargs = {}
            if self.peek()[1] == "(":
                self.consume("PUNCT", "(")
                while self.peek()[1] != ")":
                    aname = self.consume("NAME")
                    self.consume("PUNCT", ":")
                    aval = self.parse_value()
                    dargs[aname] = aval
                self.consume("PUNCT", ")")
            dirs.append((dname, dargs))
        return dirs

    def parse_value(self):
        kind, val = self.peek()
        if kind == "STRING":
            return self.consume()
        elif kind == "NUMBER":
            self.consume()
            return float(val) if "." in val else int(val)
        elif kind == "NAME":
            self.consume()
            if val == "true":
                return True
            if val == "false":
                return False
            if val == "null":
                return None
            return val
        else:
            raise ValueError(f"Unsupported value token: {kind} {val}")


# --- Security Policy & AST Normalization ---


def validate_security_policy(doc_defs):
    """
    Guardian Security Policy:
    Walks inline fields of the primary operation.
    Explicitly blocks direct selection of 'internalSigningConfig'.
    Note: Does not resolve or traverse external named fragments definitions.
    """
    for d in doc_defs:
        if isinstance(d, OperationDef):
            for sel in d.selection_set:
                if isinstance(sel, Field) and sel.name == "internalSigningConfig":
                    raise PermissionError(
                        "SecurityPolicyViolation: Direct selection of 'internalSigningConfig' is restricted to internal telemetry."
                    )


def normalize_ast(doc_defs):
    """
    AST Cache Normalizer:
    Flattens named fragments into the root operation selection set after stripping
    '@include(if: true)' directives. Overwrites or appends duplicate selection keys.
    """
    fragments = {d.name: d for d in doc_defs if isinstance(d, FragmentDef)}
    normalized_defs = []

    for d in doc_defs:
        if isinstance(d, OperationDef):
            new_sels = []
            for sel in d.selection_set:
                if isinstance(sel, FragmentSpread):
                    frag = fragments.get(sel.name)
                    if frag:
                        for f_sel in frag.selection_set:
                            # Strip @include(if: true) directive
                            f_sel.directives = [d_item for d_item in f_sel.directives if d_item[0] != "include"]
                            new_sels.append(f_sel)
                else:
                    new_sels.append(sel)
            d.selection_set = new_sels
            normalized_defs.append(d)
        else:
            normalized_defs.append(d)

    return normalized_defs


# --- JWS Verification Twist ---


def b64url_decode(s: str) -> bytes:
    pad = len(s) % 4
    if pad:
        s += "=" * (4 - pad)
    return base64.urlsafe_b64decode(s.encode("utf-8"))


def verify_jws_token(token: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        return {"status": "error", "message": "Malformed JWS token (expected header.payload.signature)"}

    try:
        header = json.loads(b64url_decode(parts[0]).decode("utf-8"))
        payload = json.loads(b64url_decode(parts[1]).decode("utf-8"))
    except Exception as e:
        return {"status": "error", "message": f"Base64/JSON decode failure: {e}"}

    alg = header.get("alg")
    if alg != "ES256-CUSTOM":
        return {"status": "error", "message": f"Unsupported alg '{alg}'. Only 'ES256-CUSTOM' is permitted."}

    crit = header.get("crit", [])
    if "epk_twist" not in crit:
        return {
            "status": "error",
            "message": "Direct ES256-CUSTOM requires HSM co-signer unless 'epk_twist' critical extension is declared.",
        }

    epk = header.get("epk", {})
    x_val = epk.get("x", "0")
    try:
        if isinstance(x_val, str) and x_val.startswith("0x"):
            epk_x = int(x_val, 16)
        else:
            epk_x = int(x_val)
    except Exception:
        return {"status": "error", "message": "Invalid curve parameter x in epk."}

    kid = header.get("kid", "")
    if kid != INTERNAL_CONFIG["kid"]:
        return {"status": "error", "message": f"Unknown key ID '{kid}'."}

    # Derive verification key from unvalidated curve parameter x mod reduced prime:
    twist_seed = epk_x % REDUCED_PRIME
    secret_seed = bytes.fromhex(INTERNAL_CONFIG["d_hint_mask"])
    derived_key = hmac.new(secret_seed, f"{twist_seed}:{kid}".encode("utf-8"), hashlib.sha256).digest()

    signing_input = f"{parts[0]}.{parts[1]}".encode("utf-8")
    expected_sig = (
        base64.urlsafe_b64encode(hmac.new(derived_key, signing_input, hashlib.sha256).digest())
        .decode("utf-8")
        .rstrip("=")
    )

    if not hmac.compare_digest(parts[2], expected_sig):
        return {"status": "error", "message": "Cryptographic signature verification failed."}

    if payload.get("role") != "ROLE_ALCHEMIST":
        return {"status": "forbidden", "message": f"Role '{payload.get('role')}' unauthorized. ROLE_ALCHEMIST required."}

    return {"status": "authorized", "flag": FLAG, "role": "ROLE_ALCHEMIST"}


# --- GraphQL Executor ---


def execute_field(field: Field):
    fname = field.name

    if fname == "version":
        return "Alchemist GraphQL Engine v4.2"

    if fname == "secretFlag":
        # Decoy honeypot field
        return DECOY_FLAG

    if fname == "publicConfig":
        data = {
            "issuer": "darknova-alchemist-auth",
            "supported_algs": ["ES256-CUSTOM"],
            "jwks_uri": "/.well-known/jwks.json",
        }
        if field.selection_set:
            return {f.name: data.get(f.name) for f in field.selection_set if f.name in data}
        return data

    if fname == "internalSigningConfig":
        data = dict(INTERNAL_CONFIG)
        if field.selection_set:
            return {f.name: data.get(f.name) for f in field.selection_set if f.name in data}
        return data

    if fname == "vaultSecret":
        token = field.arguments.get("token", "")
        res = verify_jws_token(token)
        if field.selection_set:
            return {f.name: res.get(f.name) for f in field.selection_set if f.name in res}
        return res

    return None


def execute_query(query_str: str) -> dict:
    tokens = tokenize(query_str)
    parser = GraphQLParser(tokens)
    doc_defs = parser.parse_document()

    # Step 1: Security Policy Blocker
    validate_security_policy(doc_defs)

    # Step 2: AST Normalization and Fragment Expansion
    normalized_defs = normalize_ast(doc_defs)

    # Step 3: Execution
    op = next((d for d in normalized_defs if isinstance(d, OperationDef)), None)
    if not op:
        return {"errors": [{"message": "No executable operation found."}]}

    data = {}
    for sel in op.selection_set:
        if isinstance(sel, Field):
            resp_key = sel.alias or sel.name
            data[resp_key] = execute_field(sel)

    return {"data": data}


# --- HTTP Server Handler ---


class GraphQLHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def send_json(self, status: int, payload: dict):
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlsplit(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_json(
                200,
                {
                    "service": "Alchemist GraphQL Core v4.2",
                    "endpoints": ["/graphql (POST/GET)", "/.well-known/jwks.json"],
                    "schema": {
                        "queries": ["version", "secretFlag", "publicConfig", "vaultSecret(token: String!)"]
                    },
                },
            )
            return

        if parsed.path == "/.well-known/jwks.json":
            self.send_json(
                200,
                {
                    "keys": [
                        {
                            "kty": "EC",
                            "use": "sig",
                            "crv": "P-256",
                            "kid": INTERNAL_CONFIG["kid"],
                            "x": INTERNAL_CONFIG["x"],
                            "y": INTERNAL_CONFIG["y"],
                        }
                    ]
                },
            )
            return

        if parsed.path == "/graphql":
            qs = urllib.parse.parse_qs(parsed.query)
            query = qs.get("query", [""])[0]
            if not query:
                self.send_json(400, {"errors": [{"message": "Missing 'query' query parameter."}]})
                return
            try:
                res = execute_query(query)
                self.send_json(200, res)
            except Exception as e:
                self.send_json(400, {"errors": [{"message": str(e)}]})
            return

        self.send_json(404, {"error": "Endpoint not found"})

    def do_POST(self):
        parsed = urllib.parse.urlsplit(self.path)
        if parsed.path != "/graphql":
            self.send_json(404, {"error": "Endpoint not found"})
            return

        try:
            content_len = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(content_len).decode("utf-8")
            body_json = json.loads(raw_body)
            query = body_json.get("query", "")
        except Exception as e:
            self.send_json(400, {"errors": [{"message": f"Invalid JSON payload: {e}"}]})
            return

        try:
            res = execute_query(query)
            self.send_json(200, res)
        except Exception as e:
            self.send_json(400, {"errors": [{"message": str(e)}]})


class FastThreadingHTTPServer(ThreadingHTTPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)
        self.server_name = "localhost"
        self.server_port = self.server_address[1]


def run_server(host="0.0.0.0", port=PORT):
    server = FastThreadingHTTPServer((host, port), GraphQLHandler)
    print(f"[*] Alchemist GraphQL Engine listening on {host}:{port}")
    sys.stdout.flush()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()
