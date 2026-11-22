#!/usr/bin/env python3
"""
01 — THRONE FLOOD  (variante "Colline" NCTF)
============================================================================
SCÉNARIO VISÉ
    Un service donne le "trône" (score max / contrôle) à l'équipe qui soumet
    sa preuve/son flag LE PLUS RÉCEMMENT ou LE PLUS SOUVENT. Le classement est
    recalculé en continu : dès qu'un adversaire soumet, il te passe devant, donc
    il faut ré-soumettre en boucle, le plus vite possible, et NE PAS s'arrêter.
    -> C'est exactement le type "il faut lancer un script qui envoie plusieurs
       requêtes par seconde pour prendre et garder le trône".

CE QUE FAIT CE SCRIPT
    - Envoie la même requête de soumission en boucle, avec N workers parallèles.
    - Tient le rythme cible (INTERVAL entre deux envois par worker).
    - Ne plante jamais : timeout, connexion refusée, 429 (rate-limit), 5xx gérés
      avec backoff exponentiel + jitter.
    - Détecte dans la réponse si tu tiens le trône (SUCCESS_REGEX) et logge
      ton score/position si le service le renvoie (SCORE_REGEX).
    - Affiche un résumé périodique (req/s réel, succès, échecs, 429...).

ADAPTER LE JOUR J  (modifie seulement le bloc CONFIG ci-dessous, ou via CLI)
    python3 throne_flood.py \
        --url http://10.10.10.5:1337/submit \
        --method POST \
        --data 'flag=NCTF{...}&team=1HUNTERS' \
        --workers 8 --interval 0.2

    Pour du JSON :   --json '{"flag":"NCTF{...}","team":"1HUNTERS"}'
    Pour un token :  --header 'Authorization: Bearer XXX'

Dépendance : pip install requests
============================================================================
"""

import argparse
import logging
import random
import re
import signal
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

try:
    import requests
    from requests.adapters import HTTPAdapter
except ImportError:
    sys.exit("[!] pip install requests")

# =========================================================================== #
#  CONFIG — valeurs par défaut (surchargeable en ligne de commande)           #
# =========================================================================== #
TARGET_URL    = "http://CHANGE_ME:PORT/submit"   # endpoint de soumission
METHOD        = "POST"                            # GET / POST / PUT ...
# Corps de la requête : au choix form-data, json, ou rien (GET).
SUBMIT_FORM   = {"flag": "NCTF{CHANGE_ME}", "team": "1HUNTERS"}
SUBMIT_JSON   = None                              # ex: {"flag": "...", "team": "..."}
HEADERS       = {}                                # ex: {"Authorization": "Bearer ..."}
WORKERS       = 4                                 # nb de threads parallèles
INTERVAL      = 0.5                               # secondes entre 2 envois / worker
TIMEOUT       = 5.0                               # timeout réseau (s)
MAX_RETRIES   = 3                                 # retries avant d'abandonner un envoi
BACKOFF_BASE  = 0.4                               # base du backoff exponentiel (s)
BACKOFF_MAX   = 10.0                              # plafond du backoff (s)
VERIFY_TLS    = False                             # True si certif HTTPS valide
REPORT_EVERY  = 5.0                               # résumé toutes les N secondes
# Regex appliquées au corps de la réponse pour savoir où on en est :
SUCCESS_REGEX = r"(throne|king|roi|holding|accepted|success|leader|\bok\b)"
SCORE_REGEX   = r"(?:score|points?|rank|position)[^0-9\-]{0,10}(-?\d+)"
# =========================================================================== #


class Stats:
    def __init__(self):
        self.lock = threading.Lock()
        self.sent = self.ok = self.fail = self.rl = self.net = self.throne = 0
        self.last_status = None
        self.last_score = None
        self.start = time.monotonic()

    def rec(self, **k):
        with self.lock:
            self.sent += 1
            for key in ("ok", "fail", "rl", "net", "throne"):
                if k.get(key):
                    setattr(self, key, getattr(self, key) + 1)
            if k.get("status") is not None:
                self.last_status = k["status"]
            if k.get("score") is not None:
                self.last_score = k["score"]

    def line(self):
        with self.lock:
            el = max(time.monotonic() - self.start, 1e-9)
            return (f"envoyées={self.sent} trône_ok={self.throne} échecs={self.fail} "
                    f"429={self.rl} net_err={self.net} | ~{self.sent/el:.1f} req/s "
                    f"| HTTP={self.last_status} score={self.last_score}")


STOP = threading.Event()
signal.signal(signal.SIGINT, lambda *_: STOP.set())


def make_session(cfg):
    s = requests.Session()
    a = HTTPAdapter(pool_connections=cfg.workers * 2, pool_maxsize=cfg.workers * 2)
    s.mount("http://", a)
    s.mount("https://", a)
    s.headers.update(cfg.headers)
    s.verify = cfg.verify
    return s


def sleep_backoff(attempt, cfg):
    delay = min(cfg.backoff_max, cfg.backoff_base * (2 ** attempt)) + random.uniform(0, cfg.backoff_base)
    STOP.wait(delay)


def send_once(session, cfg, log, stats):
    """Un envoi robuste. Renvoie True si le trône semble tenu."""
    attempt = 0
    while not STOP.is_set():
        try:
            resp = session.request(
                cfg.method, cfg.url, timeout=cfg.timeout,
                data=cfg.form, json=cfg.json,
            )
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            stats.rec(net=True, fail=True)
            log.debug(f"réseau: {type(e).__name__}")
            if attempt >= cfg.max_retries:
                return False
            sleep_backoff(attempt, cfg); attempt += 1; continue
        except requests.exceptions.RequestException as e:
            stats.rec(net=True, fail=True); log.debug(f"requête: {e}"); return False

        body = resp.text or ""
        if resp.status_code == 429:
            ra = resp.headers.get("Retry-After")
            wait = None
            try:
                wait = float(ra) if ra else None
            except ValueError:
                wait = 2.0
            stats.rec(rl=True, status=429)
            log.warning(f"429 rate-limit — attente {wait if wait else 'backoff'}s")
            if attempt >= cfg.max_retries:
                return False
            STOP.wait(wait) if wait else sleep_backoff(attempt, cfg)
            attempt += 1; continue

        if 500 <= resp.status_code < 600:
            stats.rec(fail=True, status=resp.status_code)
            if attempt >= cfg.max_retries:
                return False
            sleep_backoff(attempt, cfg); attempt += 1; continue

        # Réponse exploitable -> on analyse
        score = None
        m = re.search(cfg.score_regex, body, re.I)
        if m:
            try:
                score = int(m.group(1))
            except (ValueError, IndexError):
                pass
        holds = bool(re.search(cfg.success_regex, body, re.I)) and resp.status_code < 400
        stats.rec(ok=resp.status_code < 400, fail=resp.status_code >= 400,
                  throne=holds, status=resp.status_code, score=score)
        return holds


def worker(idx, cfg, log, stats):
    session = make_session(cfg)
    while not STOP.is_set():
        t0 = time.monotonic()
        try:
            held = send_once(session, cfg, log, stats)
            if held:
                log.debug(f"[w{idx}] trône tenu")
        except Exception as e:  # garde-fou : un worker ne doit jamais mourir
            log.error(f"[w{idx}] exception inattendue: {e}")
        # Respecte l'intervalle cible (sans dépasser si l'envoi a déjà pris du temps)
        remaining = cfg.interval - (time.monotonic() - t0)
        if remaining > 0:
            STOP.wait(remaining)


def reporter(cfg, log, stats):
    while not STOP.is_set():
        if STOP.wait(cfg.report_every):
            break
        log.info("STATS | " + stats.line())


def parse_args():
    p = argparse.ArgumentParser(description="Throne flood — garde le trône KOTH par ré-soumission continue")
    p.add_argument("--url", default=TARGET_URL)
    p.add_argument("--method", default=METHOD)
    p.add_argument("--data", help="corps form-urlencoded, ex: 'flag=X&team=Y' (surcharge le défaut)")
    p.add_argument("--json", help="corps JSON brut, ex: '{\"flag\":\"X\"}'")
    p.add_argument("--header", action="append", default=[], help="en-tête 'Clé: Valeur' (répétable)")
    p.add_argument("--workers", type=int, default=WORKERS)
    p.add_argument("--interval", type=float, default=INTERVAL)
    p.add_argument("--timeout", type=float, default=TIMEOUT)
    p.add_argument("--max-retries", type=int, default=MAX_RETRIES)
    p.add_argument("--backoff-base", type=float, default=BACKOFF_BASE)
    p.add_argument("--backoff-max", type=float, default=BACKOFF_MAX)
    p.add_argument("--report-every", type=float, default=REPORT_EVERY)
    p.add_argument("--verify", action="store_true", default=VERIFY_TLS)
    p.add_argument("--success-regex", default=SUCCESS_REGEX)
    p.add_argument("--score-regex", default=SCORE_REGEX)
    p.add_argument("-v", "--verbose", action="store_true")
    return p.parse_args()


def build_cfg(a):
    import json as _json
    cfg = argparse.Namespace()
    cfg.url = a.url
    cfg.method = a.method.upper()
    cfg.headers = dict(HEADERS)
    for h in a.header:
        if ":" in h:
            k, v = h.split(":", 1)
            cfg.headers[k.strip()] = v.strip()
    # Corps : CLI > constantes
    cfg.form = None
    cfg.json = None
    if a.json is not None:
        cfg.json = _json.loads(a.json)
    elif a.data is not None:
        cfg.form = dict(x.split("=", 1) for x in a.data.split("&") if "=" in x)
    elif SUBMIT_JSON is not None:
        cfg.json = SUBMIT_JSON
    elif SUBMIT_FORM is not None and cfg.method != "GET":
        cfg.form = SUBMIT_FORM
    cfg.workers = a.workers
    cfg.interval = a.interval
    cfg.timeout = a.timeout
    cfg.max_retries = a.max_retries
    cfg.backoff_base = a.backoff_base
    cfg.backoff_max = a.backoff_max
    cfg.report_every = a.report_every
    cfg.verify = a.verify
    cfg.success_regex = a.success_regex
    cfg.score_regex = a.score_regex
    return cfg


def main():
    a = parse_args()
    log = _logger(logging.DEBUG if a.verbose else logging.INFO)
    cfg = build_cfg(a)

    if "CHANGE_ME" in cfg.url:
        log.error("Configure --url (ou la constante TARGET_URL). Abandon.")
        sys.exit(2)

    log.info(f"Cible {cfg.method} {cfg.url} | {cfg.workers} workers | intervalle {cfg.interval}s")
    log.info(f"Corps: {'JSON ' + str(cfg.json) if cfg.json else ('FORM ' + str(cfg.form) if cfg.form else '(vide)')}")
    log.info("Ctrl-C pour arrêter.")

    stats = Stats()
    with ThreadPoolExecutor(max_workers=cfg.workers + 1) as pool:
        pool.submit(reporter, cfg, log, stats)
        for i in range(cfg.workers):
            pool.submit(worker, i, cfg, log, stats)
        try:
            while not STOP.is_set():
                time.sleep(0.2)
        except KeyboardInterrupt:
            STOP.set()
    log.info("Arrêt. Résumé final | " + stats.line())


def _logger(level):
    log = logging.getLogger("throne")
    log.setLevel(level)
    if not log.handlers:
        h = logging.StreamHandler()
        color = sys.stderr.isatty()
        fmt = "%(asctime)s [%(levelname)s] %(message)s"
        class F(logging.Formatter):
            C = {"DEBUG": "\033[90m", "INFO": "\033[36m", "WARNING": "\033[33m", "ERROR": "\033[31m"}
            def format(self, r):
                s = super().format(r)
                return f"{self.C.get(r.levelname,'')}{s}\033[0m" if color else s
        h.setFormatter(F(fmt, "%H:%M:%S"))
        log.addHandler(h)
    return log


if __name__ == "__main__":
    main()
