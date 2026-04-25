from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import queue


class Phase(Enum):
    PREPARE = "PREPARE"
    QUIZ    = "QUIZ"
    END     = "END"


@dataclass
class Player:
    name: str
    button_index: int   # 1–4
    score: int = 0

    @property
    def score_display(self) -> float:
        """Human-readable score — divide internal hundredths back to points."""
        return self.score / 100


class GameState:
    def __init__(self) -> None:
        self.phase         = Phase.PREPARE
        self.players       = [Player(f"Player {i}", i) for i in range(1, 5)]
        self.round_number  = 0
        self.buzzer_order: list[int] = []
        self._log: list[str]         = []
        self.buzz_queue: queue.Queue[int] = queue.Queue()   # thread-safe GPIO feed
        self.last_flash: int | None = None

    # ── Logging ──────────────────────────────────────────────────────────────

    def log(self, msg: str) -> None:
        self._log.append(msg)

    def last_log(self, n: int) -> list[str]:
        return self._log[-n:]

    # ── Lookups ──────────────────────────────────────────────────────────────

    def player(self, button_index: int) -> Optional[Player]:
        return next((p for p in self.players if p.button_index == button_index), None)

    def player_by_name(self, name: str) -> Optional[Player]:
        return next((p for p in self.players if p.name.lower() == name.lower()), None)

    # ── Phase transitions ─────────────────────────────────────────────────────

    def start_quiz(self) -> None:
        self.phase        = Phase.QUIZ
        self.round_number = 1
        self.buzzer_order = []
        self.log("Quiz started — Round 1")

    def next_round(self) -> None:
        self.round_number += 1
        self.buzzer_order = []
        self.log(f"Round {self.round_number}")

    def end_quiz(self) -> None:
        self.phase = Phase.END
        self.log("Quiz finished!")
        medals = ("1st", "2nd", "3rd", "4th")
        for i, p in enumerate(self.ranking()):
            self.log(f"  {medals[min(i,3)]}  {p.name}: {p.score_display:g} pts")

    # ── Actions ───────────────────────────────────────────────────────────────

    def register_buzz(self, button_index: int) -> None:
        p    = self.player(button_index)
        name = p.name if p else f"Button {button_index}"

        if self.phase == Phase.PREPARE:
            self.log(f"[TEST]  {name}  (B{button_index})")
            return

        if self.phase != Phase.QUIZ:
            return

        if button_index in self.buzzer_order:
            self.log(f"{name} — already buzzed this round!")
            return

        self.buzzer_order.append(button_index)
        pos = len(self.buzzer_order)
        self.log(f"#{pos}  {name}")

    def rename(self, button_index: int, name: str) -> bool:
        p = self.player(button_index)
        if not p:
            self.log(f"No button {button_index}")
            return False
        old, p.name = p.name, name
        self.log(f"Button {button_index}: '{old}' -> '{name}'")
        return True

    def adjust_score(self, name: str, delta: float) -> bool:
        p = self.player_by_name(name)
        if not p:
            return False
        p.score += round(delta * 100)   # store as integer hundredths to avoid float issues
        sign = "+" if delta >= 0 else ""
        self.log(f"{p.name}: {sign}{delta}  ->  {p.score:g} pts")
        return True

    def ranking(self) -> list[Player]:
        return sorted(self.players, key=lambda p: p.score, reverse=True)
