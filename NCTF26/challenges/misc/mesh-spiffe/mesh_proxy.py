#!/usr/bin/env python3
"""
mesh_proxy.py - Service Mesh mTLS & SPIFFE Ingress Proxy
Handles workload identity verification and downstream Vault authorization.
"""

import sys
import os
import json
import base64
import hmac
import hashlib
import posixpath
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

DECOY_FLAG = "NCTF{self_signed_cn_debug_honeypot}"
REAL_FLAG = os.environ.get("REAL_FLAG") or os.environ.get("FLAG") or "NCTF{local_test_flag_replace_with_remote}"

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bundle_config.json")

def load_bundle_config():
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"Missing config file at {CONFIG_FILE}")
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_signing_key(config):
    seed = config["attestation"]["shared_workload_seed"]
    return hashlib.sha256(seed.encode("utf-8")).digest()

def sign_svid_payload(payload_dict, config):
    key = get_signing_key(config)
    raw_json = json.dumps(payload_dict, separators=(',', ':'), sort_keys=True).encode("utf-8")
    sig = hmac.new(key, raw_json, hashlib.sha256).hexdigest()
    b64 = base64.urlsafe_b64encode(raw_json).decode("utf-8").rstrip("=")
    return f"{b64}.{sig}"

def evaluate_svid(token_str, config=None):
    """
    Evaluates an SVID token through ingress gate and downstream vault controller.
    Returns (status_code, response_dict).
    """
    if config is None:
        config = load_bundle_config()

    if not token_str or "." not in token_str:
        return 400, {"error": "Malformed SVID token format (expected <base64_payload>.<signature>)"}

    parts = token_str.strip().split(".")
    if len(parts) != 2:
        return 400, {"error": "Invalid token components"}

    payload_b64, signature = parts[0], parts[1]
    
    # Pad base64 if necessary
    padding = len(payload_b64) % 4
    if padding:
        payload_b64 += "=" * (4 - padding)

    try:
        raw_json = base64.urlsafe_b64decode(payload_b64.encode("utf-8"))
        svid = json.loads(raw_json.decode("utf-8"))
    except Exception as e:
        return 400, {"error": f"Failed to decode SVID JSON payload: {e}"}

    # Verify HMAC signature
    key = get_signing_key(config)
    expected_sig = hmac.new(key, raw_json, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected_sig):
        return 401, {"error": "Invalid SVID signature: workload attestation failure"}

    # Honeypot check: legacy Common Name (CN) debug authentication
    subject = svid.get("subject", {})
    cn = subject.get("CN", "")
    honeypot_cn = config["ingress_gateway"].get("debug_honeypot_cn", "admin.internal")
    if cn == honeypot_cn:
        return 200, {
            "status": "honeypot_triggered",
            "message": "Legacy debug administrative access granted via Common Name",
            "flag": DECOY_FLAG
        }

    # Ingress Gateway Gate: inspects primary (first) URI SAN
    san_info = svid.get("san", {})
    uris = san_info.get("uris", [])
    if not uris or not isinstance(uris, list):
        return 400, {"error": "SVID must specify at least one URI SAN"}

    ingress_san = str(uris[0])
    enforced_prefix = config["ingress_gateway"]["enforced_prefix"]
    if not ingress_san.startswith(enforced_prefix):
        return 403, {
            "error": "Ingress Gate Rejected: Primary URI SAN outside permitted sandbox",
            "inspected_san": ingress_san,
            "enforced_prefix": enforced_prefix
        }

    # Downstream Vault Policy Engine Gate:
    # Downstream service meshes or Vault policy evaluators evaluate the last identity
    vault_target_san = str(uris[-1])
    parsed = urllib.parse.urlsplit(vault_target_san)
    if parsed.scheme != "spiffe" or parsed.netloc != config["trust_domain"]:
        return 403, {"error": f"Invalid SPIFFE trust domain: {parsed.netloc}"}

    # Canonicalize path: decode percent-encoding (%2e%2e -> ..) and resolve dot segments
    decoded_path = urllib.parse.unquote(parsed.path)
    canonical_path = posixpath.normpath(decoded_path)
    canonical_principal = f"{parsed.scheme}://{parsed.netloc}{canonical_path}"

    required_principal = config["vault_policy"]["required_principal"]
    if canonical_principal != required_principal:
        return 403, {
            "error": "Vault Policy Rejected: Principal lacks vault-controller permissions",
            "resolved_principal": canonical_principal,
            "required_principal": required_principal
        }

    # Authorized!
    return 200, {
        "status": "authorized",
        "principal": canonical_principal,
        "vault_secret": REAL_FLAG
    }

class MeshProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._handle_request()

    def do_POST(self):
        self._handle_request()

    def _handle_request(self):
        token = None
        auth_header = self.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
        elif "X-SPIFFE-SVID" in self.headers:
            token = self.headers.get("X-SPIFFE-SVID", "").strip()

        status_code, body = evaluate_svid(token)
        resp_bytes = json.dumps(body, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(resp_bytes)))
        self.end_headers()
        self.wfile.write(resp_bytes)

class FastHTTPServer(HTTPServer):
    allow_reuse_address = True

    def server_bind(self):
        import socketserver
        socketserver.TCPServer.server_bind(self)
        host, port = self.server_address[:2]
        self.server_name = host
        self.server_port = port


def run_server(port=8000):
    server = FastHTTPServer(("0.0.0.0", port), MeshProxyHandler)
    print(f"[*] SPIFFE Mesh Proxy listening on port {port}...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Shutting down server.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--serve":
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
        run_server(port)
    elif len(sys.argv) > 1 and sys.argv[1] == "--eval":
        token = sys.argv[2] if len(sys.argv) > 2 else ""
        code, resp = evaluate_svid(token)
        print(f"Status Code: {code}")
        print(json.dumps(resp, indent=2))
    else:
        print(f"Usage: {sys.argv[0]} [--serve [PORT] | --eval <TOKEN>]")
