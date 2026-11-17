#!/usr/bin/env python3
"""
02 — PATCH AND DEFEND  (KOTH façon Attack / Defense)
============================================================================
SCÉNARIO VISÉ
    Chaque équipe héberge le MÊME service vulnérable. Tu marques des points en :
      (A) DÉFENDANT ton service : il doit rester UP (le checker SLA t'enlève des
          points s'il tombe) tout en étant PATCHÉ pour que les autres ne te volent
          plus ton flag ;
      (B) ATTAQUANT les services des autres équipes : voler leur flag et le
          soumettre au serveur de score, en boucle, car les flags TOURNENT à
          chaque "tick" (toutes les 1–5 min en général).

    Le classement bouge en permanence -> ce script orchestre les 3 boucles en
    parallèle : surveillance (health), défense (patch), attaque (exploit+submit).

CE QUE FAIT CE SCRIPT  (c'est un SQUELETTE à compléter)
    - Boucle DÉFENSE : vérifie périodiquement que TON service répond ; si KO ou si
      une signature de compromission apparaît, applique PATCH_COMMAND (idempotent).
    - Boucle ATTAQUE : pour chaque IP adverse, appelle exploit(ip) -> flag, puis
      submit(flag). Gère les flags déjà soumis (dédup) et les ticks.
    - Robustesse réseau partout (timeout, backoff, 429), aucun crash.

À COMPLÉTER (3 fonctions, repérées par #>>> TODO) :
    - exploit(ip)        : ton exploit réel qui renvoie le flag d'une équipe
    - health_ok()        : comment savoir que TON service va bien
    - (optionnel) apply_patch() si un simple shell command ne suffit pas

Dépendance : pip install requests
============================================================================
"""

import argparse
import logging
import random
import re
import signal
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

try:
    import requests
except ImportError:
    sys.exit("[!] pip install requests")

# =========================================================================== #
#  CONFIG                                                                      #
# =========================================================================== #
# --- Serveur de score (où soumettre les flags volés) ---
SUBMIT_URL     = "http://scoreboard:8080/api/flags"
SUBMIT_METHOD  = "POST"
SUBMIT_JSON    = True                       # True=JSON {"flag": X}, False=form
SUBMIT_FIELD   = "flag"
SUBMIT_HEADERS = {"X-Team-Token": "CHANGE_ME_TEAM_TOKEN"}
FLAG_REGEX     = r"[A-Z0-9]{31}="            # format flag A/D typique ; adapte !

# --- TES cibles adverses (les équipes à attaquer) ---
TARGETS = [
    # "10.60.1.2", "10.60.2.2", "10.60.3.2",
]
SERVICE_PORT   = 9999                        # port du service vulnérable chez chacun

# --- Défense : ton propre service ---
OWN_SERVICE_URL = "http://127.0.0.1:9999/"   # endpoint de santé local
PATCH_COMMAND   = ""                         # ex: "bash /root/patch.sh" (idempotent !)
HEALTH_SIGNATURE = ""                        # ex regex de compromission dans la page

# --- Cadence ---
ATTACK_INTERVAL  = 20.0    # secondes entre deux vagues d'attaque (≈ durée d'un tick)
DEFENSE_INTERVAL = 10.0    # secondes entre deux checks de santé
TIMEOUT          = 6.0
MAX_RETRIES      = 2
BACKOFF_BASE     = 0.5
BACKOFF_MAX      = 8.0
# =========================================================================== #

STOP = threading.Event()
signal.signal(signal.SIGINT, lambda *_: STOP.set())
_submitted = set()
_submitted_lock = threading.Lock()


# --------------------------------------------------------------------------- #
#  >>> TODO : À PERSONNALISER PAR CHALLENGE                                    #
# --------------------------------------------------------------------------- #
def exploit(ip, log):
    """
    #>>> TODO : implémente ICI l'exploit réel contre un service adverse.
    Doit renvoyer le flag (str) ou None. Exemple squelette d'exploit HTTP :
    """
    url = f"http://{ip}:{SERVICE_PORT}/vulnerable-endpoint"
    try:
        r = requests.get(url, timeout=TIMEOUT)
        m = re.search(FLAG_REGEX, r.text)
        return m.group(0) if m else None
    except requests.exceptions.RequestException as e:
        log.debug(f"exploit {ip}: {e}")
        return None


def health_ok(log):
    """
    #>>> TODO : renvoie True si TON service est sain.
    Par défaut : il répond en HTTP et ne contient pas HEALTH_SIGNATURE.
    """
    try:
        r = requests.get(OWN_SERVICE_URL, timeout=TIMEOUT)
        if r.status_code >= 500:
            return False
        if HEALTH_SIGNATURE and re.search(HEALTH_SIGNATURE, r.text):
            log.warning("Signature de compromission détectée sur ton service !")
            return False
        return True
    except requests.exceptions.RequestException:
        return False


def apply_patch(log):
    """Applique le patch défensif. DOIT être idempotent (appelé en boucle)."""
    if not PATCH_COMMAND:
        log.warning("Service KO mais PATCH_COMMAND vide — intervention manuelle requise.")
        return
    log.warning(f"Application du patch : {PATCH_COMMAND}")
    try:
        out = subprocess.run(PATCH_COMMAND, shell=True, timeout=60,
                             capture_output=True, text=True)
        log.info(f"patch rc={out.returncode} {out.stdout[-200:]} {out.stderr[-200:]}")
    except subprocess.TimeoutExpired:
        log.error("Patch : timeout.")


# --------------------------------------------------------------------------- #
#  Soumission robuste du flag                                                  #
# --------------------------------------------------------------------------- #
def submit_flag(session, flag, log):
    with _submitted_lock:
        if flag in _submitted:
            return
        _submitted.add(flag)

    attempt = 0
    while not STOP.is_set():
        try:
            kw = {"json": {SUBMIT_FIELD: flag}} if SUBMIT_JSON else {"data": {SUBMIT_FIELD: flag}}
            r = session.request(SUBMIT_METHOD, SUBMIT_URL, headers=SUBMIT_HEADERS,
                               timeout=TIMEOUT, **kw)
            if r.status_code == 429:
                _backoff(attempt); attempt += 1
                if attempt > MAX_RETRIES:
                    return
                continue
            tag = "ACCEPTÉ" if r.status_code < 400 else f"refusé({r.status_code})"
            log.info(f"FLAG {flag[:12]}… -> {tag} : {r.text[:80]}")
            return
        except requests.exceptions.RequestException as e:
            log.debug(f"submit: {e}")
            if attempt >= MAX_RETRIES:
                return
            _backoff(attempt); attempt += 1


def _backoff(attempt):
    STOP.wait(min(BACKOFF_MAX, BACKOFF_BASE * (2 ** attempt)) + random.uniform(0, BACKOFF_BASE))


# --------------------------------------------------------------------------- #
#  Boucles                                                                     #
# --------------------------------------------------------------------------- #
def defense_loop(log):
    while not STOP.is_set():
        if health_ok(log):
            log.info("DÉFENSE : service OK")
        else:
            log.error("DÉFENSE : service KO/compromis -> patch")
            apply_patch(log)
        if STOP.wait(DEFENSE_INTERVAL):
            break


def attack_loop(log):
    session = requests.Session()
    if not TARGETS:
        log.warning("ATTAQUE : TARGETS vide — remplis la liste des IPs adverses.")
    while not STOP.is_set():
        round_flags = 0
        for ip in TARGETS:
            if STOP.is_set():
                break
            flag = exploit(ip, log)
            if flag:
                round_flags += 1
                submit_flag(session, flag, log)
            else:
                log.debug(f"ATTAQUE : pas de flag depuis {ip}")
        log.info(f"ATTAQUE : vague terminée, {round_flags} flag(s) récolté(s) "
                 f"(total unique={len(_submitted)})")
        if STOP.wait(ATTACK_INTERVAL):
            break


def parse_args():
    p = argparse.ArgumentParser(description="Patch & Defend — orchestrateur KOTH attack/defense")
    p.add_argument("--targets", help="IPs adverses séparées par des virgules (surcharge TARGETS)")
    p.add_argument("--submit-url", default=SUBMIT_URL)
    p.add_argument("--attack-interval", type=float, default=ATTACK_INTERVAL)
    p.add_argument("--defense-interval", type=float, default=DEFENSE_INTERVAL)
    p.add_argument("--no-defense", action="store_true", help="ne lance que l'attaque")
    p.add_argument("--no-attack", action="store_true", help="ne lance que la défense")
    p.add_argument("-v", "--verbose", action="store_true")
    return p.parse_args()


def main():
    global TARGETS, SUBMIT_URL, ATTACK_INTERVAL, DEFENSE_INTERVAL
    a = parse_args()
    log = _logger(logging.DEBUG if a.verbose else logging.INFO)
    if a.targets:
        TARGETS = [x.strip() for x in a.targets.split(",") if x.strip()]
    SUBMIT_URL = a.submit_url
    ATTACK_INTERVAL = a.attack_interval
    DEFENSE_INTERVAL = a.defense_interval

    log.info("=== Patch & Defend ===")
    log.info(f"cibles={TARGETS or '(vide)'} | submit={SUBMIT_URL}")
    log.info(f"attaque/{ATTACK_INTERVAL}s  défense/{DEFENSE_INTERVAL}s  (Ctrl-C pour arrêter)")

    with ThreadPoolExecutor(max_workers=2) as pool:
        if not a.no_defense:
            pool.submit(defense_loop, log)
        if not a.no_attack:
            pool.submit(attack_loop, log)
        try:
            while not STOP.is_set():
                time.sleep(0.2)
        except KeyboardInterrupt:
            STOP.set()
    log.info(f"Arrêt. Flags uniques soumis : {len(_submitted)}")


def _logger(level):
    log = logging.getLogger("pad")
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
