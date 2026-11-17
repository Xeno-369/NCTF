#!/usr/bin/env python3
"""
05 — FLAG OWNERSHIP  (garder SON marqueur "king" planté)
============================================================================
SCÉNARIO VISÉ  (le KOTH "officiel" type agent CTFd / TryHackMe)
    Tu as un accès (web shell, écriture de fichier, endpoint d'écriture...) sur une
    box/un service partagé. Un AGENT vérifie périodiquement "qui est le roi" en
    lisant un MARQUEUR (un fichier, une clé, une valeur) : l'équipe dont l'identifiant
    est présent marque des points, 1 par tick de contrôle. Les adversaires écrasent
    ton marqueur par le leur -> il faut le RÉ-IMPLANTER en boucle et vérifier qu'il
    tient, pour maximiser ta durée de possession.

CE QUE FAIT CE SCRIPT (boucle plant → verify → re-plant)
    - plant()  : (re)pose ton marqueur (TODO : ton action d'écriture réelle).
    - verify() : lit le marqueur et dit s'il est TOUJOURS le tien (TODO).
    - Si perdu -> re-plant immédiat. Mesure ton % de possession (ownership).
    - Robuste : timeout, 429, erreurs réseau, backoff. Ne plante jamais.

À COMPLÉTER (#>>> TODO) :
    - plant(session)  : écrit MARKER sur la cible (POST, PUT, commande, etc.)
    - verify(session) : renvoie True si le marqueur courant == le tien

Dépendance : pip install requests
============================================================================
"""

import argparse
import logging
import random
import signal
import sys
import time

try:
    import requests
except ImportError:
    sys.exit("[!] pip install requests")

# =========================================================================== #
#  CONFIG                                                                      #
# =========================================================================== #
TARGET_BASE  = "http://CHANGE_ME:PORT"   # base de la cible
PLANT_PATH   = "/king"                    # endpoint où écrire le marqueur
VERIFY_PATH  = "/king"                    # endpoint où lire le roi courant
MARKER       = "1HUNTERS"                 # TON identifiant d'équipe (le marqueur)
PLANT_METHOD = "POST"                     # POST/PUT selon le service
PLANT_FIELD  = "owner"                    # champ qui porte le marqueur
PLANT_JSON   = False                      # True -> JSON, False -> form
HEADERS      = {}                         # ex: cookie de session, token

CHECK_INTERVAL = 1.0     # secondes entre deux cycles verify/plant
TIMEOUT        = 5.0
MAX_RETRIES    = 3
BACKOFF_BASE   = 0.4
BACKOFF_MAX    = 8.0
VERIFY_TLS     = False
REPORT_EVERY   = 10.0
# =========================================================================== #

STOP = False


def _sigint(*_):
    global STOP
    STOP = True


signal.signal(signal.SIGINT, _sigint)


# --------------------------------------------------------------------------- #
#  >>> TODO : actions réelles                                                  #
# --------------------------------------------------------------------------- #
def plant(session, log):
    """
    #>>> TODO : (re)pose TON marqueur sur la cible. Renvoie True si l'écriture a
    été acceptée. Exemple squelette (POST d'un champ 'owner') :
    """
    url = TARGET_BASE + PLANT_PATH
    try:
        kw = {"json": {PLANT_FIELD: MARKER}} if PLANT_JSON else {"data": {PLANT_FIELD: MARKER}}
        r = session.request(PLANT_METHOD, url, timeout=TIMEOUT, **kw)
        return r.status_code < 400
    except requests.exceptions.RequestException as e:
        log.debug(f"plant: {e}")
        return False


def verify(session, log):
    """
    #>>> TODO : lis le roi courant et renvoie True s'il s'agit de TOI (MARKER).
    Exemple squelette (GET + recherche du marqueur dans la réponse) :
    """
    url = TARGET_BASE + VERIFY_PATH
    try:
        r = session.get(url, timeout=TIMEOUT)
        return MARKER in (r.text or "")
    except requests.exceptions.RequestException as e:
        log.debug(f"verify: {e}")
        return None  # inconnu (erreur réseau)


# --------------------------------------------------------------------------- #
#  Boucle principale                                                           #
# --------------------------------------------------------------------------- #
def robust_plant(session, log):
    """plant() avec retries/backoff."""
    for attempt in range(MAX_RETRIES + 1):
        if STOP:
            return False
        if plant(session, log):
            return True
        delay = min(BACKOFF_MAX, BACKOFF_BASE * (2 ** attempt)) + random.uniform(0, BACKOFF_BASE)
        time.sleep(delay)
    return False


def main():
    a = parse_args()
    log = _logger(logging.DEBUG if a.verbose else logging.INFO)
    globals().update({
        "TARGET_BASE": a.base or TARGET_BASE,
        "MARKER": a.marker or MARKER,
        "CHECK_INTERVAL": a.interval,
    })
    if "CHANGE_ME" in TARGET_BASE:
        log.error("Configure --base (ou TARGET_BASE). Abandon."); sys.exit(2)

    session = requests.Session()
    session.headers.update(HEADERS)
    session.verify = VERIFY_TLS

    log.info(f"Flag ownership | cible {TARGET_BASE} | marqueur '{MARKER}' | cycle {CHECK_INTERVAL}s")
    log.info("Ctrl-C pour arrêter.")

    cycles = held = lost = replants = 0
    last_report = time.monotonic()

    # Pose initiale
    if robust_plant(session, log):
        log.info("Marqueur posé initialement.")
    else:
        log.warning("Échec de la pose initiale (on retentera à chaque cycle).")

    while not STOP:
        t0 = time.monotonic()
        cycles += 1
        state = verify(session, log)
        if state is True:
            held += 1
            log.debug("roi = NOUS ✓")
        elif state is False:
            lost += 1
            log.warning("marqueur écrasé -> re-plant")
            if robust_plant(session, log):
                replants += 1
        else:
            log.debug("verify indéterminé (réseau) ; re-plant par sécurité")
            robust_plant(session, log)

        now = time.monotonic()
        if now - last_report >= REPORT_EVERY:
            own = (held / cycles * 100) if cycles else 0
            log.info(f"STATS | cycles={cycles} possession={own:.0f}% "
                     f"perdus={lost} replants={replants}")
            last_report = now

        remaining = CHECK_INTERVAL - (time.monotonic() - t0)
        if remaining > 0:
            # sommeil interruptible
            end = time.monotonic() + remaining
            while not STOP and time.monotonic() < end:
                time.sleep(min(0.1, end - time.monotonic()))

    own = (held / cycles * 100) if cycles else 0
    log.info(f"Arrêt. Possession finale ~{own:.0f}% sur {cycles} cycles "
             f"({replants} re-implantations).")


def parse_args():
    p = argparse.ArgumentParser(description="Flag ownership — garde ton marqueur 'king' planté")
    p.add_argument("--base", help="base de la cible, ex http://10.10.10.5:9000")
    p.add_argument("--marker", help="ton identifiant d'équipe (marqueur)")
    p.add_argument("--interval", type=float, default=CHECK_INTERVAL)
    p.add_argument("-v", "--verbose", action="store_true")
    return p.parse_args()


def _logger(level):
    log = logging.getLogger("own")
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
