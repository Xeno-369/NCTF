#!/usr/bin/env python3
"""
04 — API RATE OPTIMIZER  (débit maximal SANS se faire rate-limiter)
============================================================================
SCÉNARIO VISÉ
    Le trône KOTH se tient via une API web protégée par un RATE-LIMIT. Trop lent =
    un adversaire te double ; trop rapide = HTTP 429 / ban temporaire et tu perds
    des cycles. Il faut donc trouver et TENIR le débit maximal soutenable.

STRATÉGIE : contrôleur adaptatif AIMD (comme TCP)
    - Additive Increase : tant que ça passe, on augmente doucement le débit.
    - Multiplicative Decrease : au moindre 429, on divise le débit et on respecte
      `Retry-After`. Puis on remonte prudemment.
    -> Le script converge tout seul vers le débit juste sous la limite, et s'adapte
       si la limite change en cours de partie.

CE QUE FAIT CE SCRIPT
    - Envoie l'action KOTH (ex: re-soumission) en continu, au débit piloté par AIMD.
    - Respecte `Retry-After` et recule sur 429 ; backoff sur erreurs réseau/5xx.
    - Affiche en direct : débit courant (req/s), succès, 429, taux de 429.
    - 100 % stdlib + requests ; aucun crash sur erreur réseau.

ADAPTER (bloc CONFIG ou CLI) : URL, méthode, corps, headers, bornes de débit.

Dépendance : pip install requests
============================================================================
"""

import argparse
import logging
import random
import signal
import sys
import threading
import time

try:
    import requests
    from requests.adapters import HTTPAdapter
except ImportError:
    sys.exit("[!] pip install requests")

# =========================================================================== #
#  CONFIG                                                                      #
# =========================================================================== #
TARGET_URL   = "http://CHANGE_ME:PORT/action"
METHOD       = "POST"
FORM         = {"flag": "NCTF{CHANGE_ME}", "team": "1HUNTERS"}
JSON         = None
HEADERS      = {}

START_RPS    = 2.0      # débit initial (requêtes/seconde)
MIN_RPS      = 0.5      # plancher
MAX_RPS      = 50.0     # plafond de sécurité (ne vise jamais au-dessus)
INCREASE_STEP = 0.5     # +X req/s après une fenêtre sans 429 (additive increase)
DECREASE_FACTOR = 0.5   # xX req/s sur un 429 (multiplicative decrease)
PROBE_WINDOW = 3.0      # on tente d'augmenter toutes les N secondes "propres"
CONCURRENCY  = 4        # nb de workers (parallélisme pour tenir les hauts débits)

TIMEOUT      = 5.0
VERIFY_TLS   = False
REPORT_EVERY = 5.0
# =========================================================================== #

STOP = threading.Event()
signal.signal(signal.SIGINT, lambda *_: STOP.set())


class RateController:
    """Contrôleur AIMD thread-safe : donne le délai à respecter entre 2 envois."""
    def __init__(self, start, lo, hi, inc, dec, probe):
        self.lock = threading.Lock()
        self.rps = max(lo, min(hi, start))
        self.lo, self.hi, self.inc, self.dec, self.probe = lo, hi, inc, dec, probe
        self.last_increase = time.monotonic()
        self.retry_until = 0.0           # si >now : on est en pénalité 429

    def interval(self):
        with self.lock:
            return 1.0 / max(self.rps, 1e-6)

    def on_success(self):
        with self.lock:
            now = time.monotonic()
            if now >= self.retry_until and (now - self.last_increase) >= self.probe:
                self.rps = min(self.hi, self.rps + self.inc)
                self.last_increase = now

    def on_rate_limit(self, retry_after=None):
        with self.lock:
            self.rps = max(self.lo, self.rps * self.dec)
            self.last_increase = time.monotonic()
            if retry_after:
                self.retry_until = time.monotonic() + retry_after

    def penalty_wait(self):
        with self.lock:
            return max(0.0, self.retry_until - time.monotonic())

    def current(self):
        with self.lock:
            return self.rps


class Stats:
    def __init__(self):
        self.lock = threading.Lock()
        self.sent = self.ok = self.rl = self.err = 0
        self.start = time.monotonic()

    def rec(self, ok=False, rl=False, err=False):
        with self.lock:
            self.sent += 1
            self.ok += int(ok); self.rl += int(rl); self.err += int(err)

    def line(self, ctrl):
        with self.lock:
            el = max(time.monotonic() - self.start, 1e-9)
            pct429 = (self.rl / self.sent * 100) if self.sent else 0
            return (f"débit_cible={ctrl.current():.1f} req/s réel={self.sent/el:.1f} | "
                    f"ok={self.ok} 429={self.rl} ({pct429:.0f}%) net_err={self.err}")


def make_session():
    s = requests.Session()
    a = HTTPAdapter(pool_connections=CONCURRENCY * 2, pool_maxsize=CONCURRENCY * 2)
    s.mount("http://", a); s.mount("https://", a)
    s.headers.update(HEADERS); s.verify = VERIFY_TLS
    return s


def worker(cfg, ctrl, stats, log):
    session = make_session()
    while not STOP.is_set():
        pen = ctrl.penalty_wait()
        if pen > 0:
            if STOP.wait(min(pen, 2.0)):
                break
            continue
        t0 = time.monotonic()
        try:
            r = session.request(cfg.method, cfg.url, timeout=cfg.timeout,
                               data=cfg.form, json=cfg.json)
            if r.status_code == 429:
                ra = r.headers.get("Retry-After")
                try:
                    ra = float(ra) if ra else None
                except ValueError:
                    ra = 2.0
                ctrl.on_rate_limit(ra)
                stats.rec(rl=True)
                log.warning(f"429 -> débit réduit à {ctrl.current():.1f} req/s"
                            + (f" (Retry-After {ra}s)" if ra else ""))
            elif 500 <= r.status_code < 600:
                stats.rec(err=True)
                ctrl.on_rate_limit(None)  # on lève aussi le pied sur 5xx
            else:
                stats.rec(ok=r.status_code < 400)
                ctrl.on_success()
        except requests.exceptions.RequestException as e:
            stats.rec(err=True)
            log.debug(f"réseau: {type(e).__name__}")
            STOP.wait(0.5 + random.uniform(0, 0.5))
            continue
        # Pacing : respecte l'intervalle divisé par le nb de workers
        target = ctrl.interval() * cfg.concurrency
        remaining = target - (time.monotonic() - t0)
        if remaining > 0:
            STOP.wait(remaining)


def reporter(cfg, ctrl, stats, log):
    while not STOP.is_set():
        if STOP.wait(cfg.report_every):
            break
        log.info("STATS | " + stats.line(ctrl))


def main():
    a = parse_args()
    log = _logger(logging.DEBUG if a.verbose else logging.INFO)
    cfg = argparse.Namespace(
        url=a.url, method=a.method.upper(), form=FORM if JSON is None else None,
        json=JSON, timeout=a.timeout, concurrency=a.concurrency,
        report_every=REPORT_EVERY,
    )
    if "CHANGE_ME" in cfg.url:
        log.error("Configure --url (ou TARGET_URL). Abandon."); sys.exit(2)

    ctrl = RateController(a.start_rps, a.min_rps, a.max_rps,
                          a.increase, a.decrease, a.probe)
    stats = Stats()
    log.info(f"AIMD rate optimizer -> {cfg.method} {cfg.url}")
    log.info(f"débit {a.start_rps}→[{a.min_rps};{a.max_rps}] req/s | {a.concurrency} workers")
    log.info("Ctrl-C pour arrêter.")

    threads = [threading.Thread(target=reporter, args=(cfg, ctrl, stats, log), daemon=True)]
    for _ in range(a.concurrency):
        threads.append(threading.Thread(target=worker, args=(cfg, ctrl, stats, log), daemon=True))
    for t in threads:
        t.start()
    try:
        while not STOP.is_set():
            time.sleep(0.2)
    except KeyboardInterrupt:
        STOP.set()
    STOP.set()
    log.info("Arrêt. Résumé final | " + stats.line(ctrl))


def parse_args():
    p = argparse.ArgumentParser(description="Optimiseur de débit AIMD face au rate-limit")
    p.add_argument("--url", default=TARGET_URL)
    p.add_argument("--method", default=METHOD)
    p.add_argument("--start-rps", type=float, default=START_RPS)
    p.add_argument("--min-rps", type=float, default=MIN_RPS)
    p.add_argument("--max-rps", type=float, default=MAX_RPS)
    p.add_argument("--increase", type=float, default=INCREASE_STEP)
    p.add_argument("--decrease", type=float, default=DECREASE_FACTOR)
    p.add_argument("--probe", type=float, default=PROBE_WINDOW)
    p.add_argument("--concurrency", type=int, default=CONCURRENCY)
    p.add_argument("--timeout", type=float, default=TIMEOUT)
    p.add_argument("-v", "--verbose", action="store_true")
    return p.parse_args()


def _logger(level):
    log = logging.getLogger("rate")
    log.setLevel(level)
    if not log.handlers:
        h = logging.StreamHandler()
        color = sys.stderr.isatty()
        class F(logging.Formatter):
            C = {"DEBUG": "\033[90m", "INFO": "\033[36m", "WARNING": "\033[33m", "ERROR": "\033[31m"}
            def format(self, r):
                s = super().format(r)
                return f"{self.C.get(r.levelname,'')}{s}\033[0m" if color else s
        h.setFormatter(F("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S"))
        log.addHandler(h)
    return log


if __name__ == "__main__":
    main()
