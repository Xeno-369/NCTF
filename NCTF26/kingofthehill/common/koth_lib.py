#!/usr/bin/env python3
"""
koth_lib.py — Boîte à outils commune pour les scripts King of the Hill (NCTF26 / 1HUNTERS)
===========================================================================================

Ce module regroupe la "plomberie" robuste réutilisée par toutes les variantes KOTH :
  - une session HTTP persistante (keep-alive) avec pool de connexions,
  - un envoi de requête `robust_request()` qui ne plante JAMAIS :
      * gère timeout, connexion refusée, erreurs réseau,
      * gère HTTP 429 (rate-limit) en respectant l'en-tête `Retry-After`,
      * gère les 5xx,
      * backoff exponentiel + jitter configurable,
  - des compteurs de statistiques thread-safe (`Stats`),
  - un logger lisible (horodaté, couleurs si terminal),
  - un gestionnaire de Ctrl-C propre (`StopFlag`).

USAGE
-----
Les scripts de chaque variante sont AUTONOMES (ils recopient ces helpers) pour que tu
puisses copier UN seul fichier sur une box le jour J. Ce module est fourni en plus, si tu
préfères écrire un script custom sans dupliquer la plomberie :

    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
    from koth_lib import make_session, robust_request, Stats, get_logger, StopFlag

Dépendance : `pip install requests`
"""

import logging
import random
import signal
import threading
import time

try:
    import requests
    from requests.adapters import HTTPAdapter
except ImportError:  # pragma: no cover
    raise SystemExit("[!] Dépendance manquante : pip install requests")


# --------------------------------------------------------------------------- #
#  Logger                                                                      #
# --------------------------------------------------------------------------- #
class _ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[90m", "INFO": "\033[36m", "WARNING": "\033[33m",
        "ERROR": "\033[31m", "CRITICAL": "\033[41m",
    }
    RESET = "\033[0m"

    def __init__(self, use_color=True):
        super().__init__("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S")
        self.use_color = use_color

    def format(self, record):
        msg = super().format(record)
        if self.use_color:
            color = self.COLORS.get(record.levelname, "")
            msg = f"{color}{msg}{self.RESET}"
        return msg


def get_logger(name="koth", level=logging.INFO, use_color=None):
    """Logger horodaté, coloré si on écrit vers un vrai terminal."""
    import sys
    if use_color is None:
        use_color = sys.stderr.isatty()
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        h = logging.StreamHandler()
        h.setFormatter(_ColorFormatter(use_color))
        logger.addHandler(h)
    return logger


# --------------------------------------------------------------------------- #
#  Arrêt propre (Ctrl-C)                                                       #
# --------------------------------------------------------------------------- #
class StopFlag:
    """Drapeau partagé entre workers, basculé proprement sur SIGINT/SIGTERM."""
    def __init__(self):
        self._event = threading.Event()
        signal.signal(signal.SIGINT, self._handler)
        try:
            signal.signal(signal.SIGTERM, self._handler)
        except (ValueError, OSError):
            pass  # SIGTERM indisponible hors thread principal

    def _handler(self, signum, frame):
        self._event.set()

    def is_set(self):
        return self._event.is_set()

    def wait(self, seconds):
        """Attend `seconds`, mais s'interrompt immédiatement si on demande l'arrêt."""
        return self._event.wait(seconds)


# --------------------------------------------------------------------------- #
#  Statistiques thread-safe                                                    #
# --------------------------------------------------------------------------- #
class Stats:
    def __init__(self):
        self._lock = threading.Lock()
        self.sent = 0
        self.ok = 0
        self.fail = 0
        self.rate_limited = 0
        self.net_err = 0
        self.start = time.monotonic()
        self.last_status = None

    def record(self, *, ok=False, fail=False, rate_limited=False, net_err=False, status=None):
        with self._lock:
            self.sent += 1
            if ok:
                self.ok += 1
            if fail:
                self.fail += 1
            if rate_limited:
                self.rate_limited += 1
            if net_err:
                self.net_err += 1
            if status is not None:
                self.last_status = status

    def snapshot(self):
        with self._lock:
            elapsed = max(time.monotonic() - self.start, 1e-9)
            return {
                "sent": self.sent, "ok": self.ok, "fail": self.fail,
                "rate_limited": self.rate_limited, "net_err": self.net_err,
                "elapsed": elapsed, "rps": self.sent / elapsed,
                "last_status": self.last_status,
            }

    def line(self):
        s = self.snapshot()
        return (f"envoyées={s['sent']} ok={s['ok']} échecs={s['fail']} "
                f"429={s['rate_limited']} net_err={s['net_err']} "
                f"~{s['rps']:.1f} req/s (dernier HTTP={s['last_status']})")


# --------------------------------------------------------------------------- #
#  Session HTTP persistante                                                    #
# --------------------------------------------------------------------------- #
def make_session(pool=32, headers=None, verify=True):
    """Session requests avec keep-alive et un grand pool de connexions."""
    s = requests.Session()
    adapter = HTTPAdapter(pool_connections=pool, pool_maxsize=pool, max_retries=0)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    if headers:
        s.headers.update(headers)
    s.verify = verify
    return s


# --------------------------------------------------------------------------- #
#  Envoi robuste                                                               #
# --------------------------------------------------------------------------- #
def robust_request(session, method, url, *, logger=None, stats=None, stop=None,
                   max_retries=4, backoff_base=0.5, backoff_max=15.0,
                   timeout=5.0, respect_retry_after=True, **kwargs):
    """
    Envoie une requête et renvoie (response | None).

    - Ne lève jamais d'exception réseau : renvoie None en cas d'échec définitif.
    - Retry avec backoff exponentiel + jitter sur : timeout, erreur de connexion,
      HTTP 429 et HTTP 5xx.
    - Respecte `Retry-After` sur un 429 si présent.
    - `stop` (StopFlag) interrompt l'attente de backoff immédiatement.
    """
    attempt = 0
    while True:
        if stop is not None and stop.is_set():
            return None
        try:
            resp = session.request(method, url, timeout=timeout, **kwargs)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            if stats:
                stats.record(net_err=True, fail=True)
            if logger:
                logger.debug(f"erreur réseau: {type(e).__name__}")
            if attempt >= max_retries:
                return None
            _sleep_backoff(attempt, backoff_base, backoff_max, stop)
            attempt += 1
            continue
        except requests.exceptions.RequestException as e:
            if stats:
                stats.record(net_err=True, fail=True)
            if logger:
                logger.debug(f"erreur requête: {e}")
            return None

        # Rate-limit
        if resp.status_code == 429:
            if stats:
                stats.record(rate_limited=True, status=429)
            wait = _retry_after(resp) if respect_retry_after else None
            if logger:
                logger.warning(f"429 rate-limit (attente {wait if wait else 'backoff'}s)")
            if attempt >= max_retries:
                return resp
            if wait is not None and stop is not None:
                stop.wait(wait)
            elif wait is not None:
                time.sleep(wait)
            else:
                _sleep_backoff(attempt, backoff_base, backoff_max, stop)
            attempt += 1
            continue

        # Erreurs serveur : on retente
        if 500 <= resp.status_code < 600:
            if stats:
                stats.record(fail=True, status=resp.status_code)
            if attempt >= max_retries:
                return resp
            _sleep_backoff(attempt, backoff_base, backoff_max, stop)
            attempt += 1
            continue

        # Réponse exploitable
        if stats:
            stats.record(ok=(resp.status_code < 400), fail=(resp.status_code >= 400),
                         status=resp.status_code)
        return resp


def _retry_after(resp):
    ra = resp.headers.get("Retry-After")
    if not ra:
        return None
    try:
        return max(0.0, float(ra))
    except ValueError:
        # Format HTTP-date : on retombe sur une attente par défaut
        return 2.0


def _sleep_backoff(attempt, base, cap, stop=None):
    delay = min(cap, base * (2 ** attempt))
    delay += random.uniform(0, base)  # jitter anti-synchronisation
    if stop is not None:
        stop.wait(delay)
    else:
        time.sleep(delay)
