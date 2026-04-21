"""
Parse and execute host commands typed in the input bar.
"""
from __future__ import annotations
import re
from game import GameState, Phase


def process(game: GameState, cmd: str) -> None:
    """Mutates game state based on cmd string. Logs errors back into game."""
    raw = cmd.strip()
    low = raw.lower()

    if not raw:
        return

    # ── start ────────────────────────────────────────────────────────────────
    if low == "start":
        if game.phase == Phase.PREPARE:
            game.start_quiz()
        else:
            game.log("Already started.")
        return

    # ── next / n ─────────────────────────────────────────────────────────────
    if low in ("next", "n"):
        if game.phase == Phase.QUIZ:
            game.next_round()
        else:
            game.log("Not in quiz mode.")
        return

    # ── end / e ──────────────────────────────────────────────────────────────
    if low in ("end", "e"):
        if game.phase == Phase.QUIZ:
            game.end_quiz()
        else:
            game.log("Not in quiz mode.")
        return

    # ── b1–b4  (simulate buzzer, dev / testing without hardware) ─────────────
    m = re.match(r'^b([1-4])$', low)
    if m:
        game.register_buzz(int(m.group(1)))
        return

    # ── name <1-4> <Name> ────────────────────────────────────────────────────
    m = re.match(r'^name\s+([1-4])\s+(.+)$', raw, re.IGNORECASE)
    if m:
        game.rename(int(m.group(1)), m.group(2).strip())
        return

    # ── <Name> +N / -N  e.g. "Alice +1", "Bob -2" ───────────────────────────
    m = re.match(r'^(.+?)\s*([+-]\d+)\s*$', raw)
    if m:
        name, delta = m.group(1).strip(), int(m.group(2))
        if not game.adjust_score(name, delta):
            game.log(f"Player '{name}' not found.")
        return

    game.log(f"Unknown command: {raw}")
