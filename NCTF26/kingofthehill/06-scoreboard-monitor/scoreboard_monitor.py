#!/usr/bin/env python3
"""
06 — SCOREBOARD MONITOR  (suivi live du classement + alertes)
============================================================================
RÔLE
    Script COMPAGNON des autres variantes : il interroge le scoreboard en boucle,
    affiche TON rang, TON score, l'écart avec le leader, et t'ALERTE (son + log
    rouge) dès que tu perds la tête ou que tu chutes. Indispensable pour piloter
    en live le débit de 01/04 ou l'agressivité de 05.

MODES DE PARSING (au choix selon le service)
    - JSON  : le scoreboard renvoie une liste d'entrées {nom, score}. Tu donnes les
              noms de champs (--name-field / --score-field) ; auto-détection sinon.
    - REGEX : le scoreboard est en HTML. Tu donnes une regex à 2 groupes (nom, score).

ROBUSTE : timeout, 429, erreurs réseau, backoff ; ne plante jamais.

ADAPTER : --url du scoreboard, --team (ton nom exact tel qu'affiché).

Dépendance : pip install requests
============================================================================
"""

import argparse
import json
import logging
import re
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
SCOREBOARD_URL = "http://CHANGE_ME:PORT/api/scoreboard"
TEAM_NAME      = "1HUNTERS"
HEADERS        = {}
POLL_INTERVAL  = 5.0
TIMEOUT        = 6.0
# JSON : noms des champs (laisse None pour auto-détection)
NAME_FIELD     = None      # ex: "name" / "team" / "username"
SCORE_FIELD    = None      # ex: "score" / "points"
# REGEX (mode HTML) : 2 groupes = (nom, score). None = mode JSON.
HTML_REGEX     = None      # ex: r'<td>([^<]+)</td>\s*<td>(\d+)</td>'
VERIFY_TLS     = False
# =========================================================================== #

STOP = False
signal.signal(signal.SIGINT, lambda *_: globals().__setitem__("STOP", True))

NAME_CANDIDATES  = ["name", "team", "team_name", "teamname", "username", "user", "player"]
SCORE_CANDIDATES = ["score", "points", "pts", "total", "value"]


def fetch(session, url, log):
    try:
        r = session.get(url, timeout=TIMEOUT)
        if r.status_code == 429:
            ra = r.headers.get("Retry-After")
            log.warning(f"429 sur le scoreboard (Retry-After={ra})")
            return None
        if r.status_code >= 400:
            log.debug(f"scoreboard HTTP {r.status_code}")
            return None
        return r
    except requests.exceptions.RequestException as e:
        log.debug(f"réseau: {e}")
        return None


def _find_entries(obj):
    """Trouve récursivement la 1re liste de dicts qui ressemble à un classement."""
    if isinstance(obj, list) and obj and isinstance(obj[0], dict):
        return obj
    if isinstance(obj, dict):
        for v in obj.values():
            found = _find_entries(v)
            if found:
                return found
    return None


def parse_json(text, name_field, score_field, log):
    try:
        data = json.loads(text)
    except ValueError:
        return None
    entries = _find_entries(data)
    if not entries:
        return None
    nf = name_field or next((c for c in NAME_CANDIDATES if c in entries[0]), None)
    sf = score_field or next((c for c in SCORE_CANDIDATES if c in entries[0]), None)
    if not nf or not sf:
        log.debug(f"champs non trouvés (clés dispo: {list(entries[0].keys())})")
        return None
    out = []
    for e in entries:
        try:
            out.append((str(e[nf]), float(e[sf])))
        except (KeyError, ValueError, TypeError):
            continue
    return out or None


def parse_html(text, regex, log):
    out = []
    for m in re.finditer(regex, text, re.I | re.S):
        try:
            out.append((m.group(1).strip(), float(re.sub(r"[^\d.\-]", "", m.group(2)))))
        except (IndexError, ValueError):
            continue
    return out or None


def rank_board(board):
    """Trie par score décroissant, renvoie [(rang, nom, score)]."""
    s = sorted(board, key=lambda x: x[1], reverse=True)
    return [(i + 1, n, sc) for i, (n, sc) in enumerate(s)]


def main():
    a = parse_args()
    log = _logger(logging.DEBUG if a.verbose else logging.INFO)
    url = a.url or SCOREBOARD_URL
    team = a.team or TEAM_NAME
    if "CHANGE_ME" in url:
        log.error("Configure --url (ou SCOREBOARD_URL). Abandon."); sys.exit(2)

    session = requests.Session()
    session.headers.update(HEADERS)
    session.verify = VERIFY_TLS

    log.info(f"Scoreboard monitor | {url} | équipe '{team}' | poll {a.interval}s")
    log.info("Ctrl-C pour arrêter.")

    prev_rank = None
    while not STOP:
        t0 = time.monotonic()
        r = fetch(session, url, log)
        if r is not None:
            board = (parse_html(r.text, a.regex, log) if a.regex
                     else parse_json(r.text, a.name_field, a.score_field, log))
            if not board:
                log.warning("Impossible de parser le scoreboard "
                            "(essaie --regex, ou --name-field/--score-field).")
            else:
                ranked = rank_board(board)
                me = next((row for row in ranked if row[1].lower() == team.lower()), None)
                leader = ranked[0]
                if me is None:
                    log.warning(f"'{team}' absent du classement. Leader: "
                                f"{leader[1]} ({leader[2]:.0f})")
                else:
                    rank, _, score = me
                    gap = leader[2] - score
                    status = "👑 LEADER" if rank == 1 else f"écart au 1er={gap:.0f}"
                    line = (f"rang={rank}/{len(ranked)} score={score:.0f} | {status} "
                            f"| 1er={leader[1]}({leader[2]:.0f})")
                    # Alerte si on perd la tête ou si on recule
                    if prev_rank is not None and rank > prev_rank:
                        log.error(f"\a⚠️  TU RECULES ({prev_rank}->{rank}) ! {line}")
                    elif rank == 1 and prev_rank != 1:
                        log.info(f"\a✅ TÊTE REPRISE ! {line}")
                    else:
                        log.info(line)
                    prev_rank = rank
        remaining = a.interval - (time.monotonic() - t0)
        if remaining > 0:
            end = time.monotonic() + remaining
            while not STOP and time.monotonic() < end:
                time.sleep(min(0.1, end - time.monotonic()))
    log.info("Arrêt du monitoring.")


def parse_args():
    p = argparse.ArgumentParser(description="Moniteur de scoreboard KOTH (rang, écart, alertes)")
    p.add_argument("--url", help="URL du scoreboard (API JSON ou page HTML)")
    p.add_argument("--team", help="ton nom d'équipe exact tel qu'affiché")
    p.add_argument("--interval", type=float, default=POLL_INTERVAL)
    p.add_argument("--name-field", default=NAME_FIELD, help="JSON: champ du nom")
    p.add_argument("--score-field", default=SCORE_FIELD, help="JSON: champ du score")
    p.add_argument("--regex", default=HTML_REGEX, help="HTML: regex 2 groupes (nom, score)")
    p.add_argument("-v", "--verbose", action="store_true")
    return p.parse_args()


def _logger(level):
    log = logging.getLogger("score")
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
