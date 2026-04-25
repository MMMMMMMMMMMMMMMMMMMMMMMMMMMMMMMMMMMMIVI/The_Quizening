"""
All curses drawing logic.
One draw_* function per screen region; each takes its window + data, erases,
redraws, and refreshes. Nothing in here touches game state directly — it only
reads what it is passed.
"""
from __future__ import annotations
import curses
from game import GameState, Phase, Player

# ── Color pair IDs ────────────────────────────────────────────────────────────
C_P1        = 1   # player 1 — cyan
C_P2        = 2   # player 2 — green
C_P3        = 3   # player 3 — yellow
C_P4        = 4   # player 4 — magenta
C_TITLE     = 5   # title bar  (white on blue)
C_ACCENT    = 6   # prompts / borders — blue fg
C_DIM       = 7   # log lines — dark / dim
C_SUCCESS   = 8   # green fg  (1st buzz)
C_WARN      = 9   # yellow fg (2nd buzz)
C_INPUT     = 10  # input prompt

PLAYER_COLORS = [C_P1, C_P2, C_P3, C_P4]
BUZZ_COLORS   = [C_SUCCESS, C_WARN, C_P1, C_DIM]
MEDALS        = ("1.", "2.", "3.", "4.")


def init_colors() -> None:
    curses.start_color()
    curses.use_default_colors()          # -1 = terminal's own background
    curses.init_pair(C_P1,     curses.COLOR_BLUE,    -1)
    curses.init_pair(C_P2,     curses.COLOR_GREEN,   -1)
    curses.init_pair(C_P3,     curses.COLOR_YELLOW,  -1)
    curses.init_pair(C_P4,     curses.COLOR_RED, -1)
    curses.init_pair(C_TITLE,  curses.COLOR_WHITE,   curses.COLOR_BLUE)
    curses.init_pair(C_ACCENT, curses.COLOR_BLUE,    -1)
    curses.init_pair(C_DIM,    curses.COLOR_WHITE,   -1)
    curses.init_pair(C_SUCCESS,curses.COLOR_GREEN,   -1)
    curses.init_pair(C_WARN,   curses.COLOR_YELLOW,  -1)
    curses.init_pair(C_INPUT,  curses.COLOR_CYAN,    -1)


# ── Layout ────────────────────────────────────────────────────────────────────

SCORE_H = 5    # title row + blank + name row + score row + divider
LOG_H   = 26    # 1 header row + 25 log lines
INPUT_H = 1    # single command line at the bottom


def create_windows(stdscr):
    """Return (win_scores, win_main, win_log, win_input). Call again on resize."""
    curses.halfdelay(1)
    rows, cols = stdscr.getmaxyx()
    main_h = max(3, rows - SCORE_H - LOG_H - INPUT_H)

    win_scores = curses.newwin(SCORE_H, cols, 0,                          0)
    win_main   = curses.newwin(main_h,  cols, SCORE_H,                    0)
    win_log    = curses.newwin(LOG_H,   cols, SCORE_H + main_h,           0)
    win_input  = curses.newwin(INPUT_H, cols, SCORE_H + main_h + LOG_H,   0)
    return win_scores, win_main, win_log, win_input


# ── Helpers ───────────────────────────────────────────────────────────────────

def _hline(win, y: int, char=None) -> None:
    if char is None:
        char = curses.ACS_HLINE
    """Draw a full-width horizontal line at row y."""
    _, cols = win.getmaxyx()
    try:
        win.hline(y, 0, char, cols)
    except curses.error:
        pass   # writing to the very last cell of a window raises; safe to ignore


def _addstr_safe(win, y: int, x: int, text: str, attr: int = 0) -> None:
    """addstr that silently skips if out of bounds."""
    rows, cols = win.getmaxyx()
    if y >= rows or x >= cols:
        return
    max_len = cols - x
    try:
        win.addstr(y, x, text[:max_len], attr)
    except curses.error:
        pass


# ── draw_scores ───────────────────────────────────────────────────────────────

def draw_scores(win, players: list[Player], flash_idx: int | None = None) -> None:
    win.erase()
    rows, cols = win.getmaxyx()

    # Title bar (row 0)
    win.bkgdset(" ", curses.color_pair(C_TITLE))
    _addstr_safe(win, 0, 0, " " * cols, curses.color_pair(C_TITLE))
    title = "  THE QUIZENING"
    _addstr_safe(win, 0, 0, title, curses.color_pair(C_TITLE) | curses.A_BOLD)
    hint = "ctrl+c to quit  "
    _addstr_safe(win, 0, cols - len(hint), hint, curses.color_pair(C_TITLE))

    # Reset background
    win.bkgdset(" ", 0)

    # Player cards (rows 2–3)
    n = len(players)
    card_w = cols // n

    for i, p in enumerate(players):
        x      = i * card_w
        attr   = curses.color_pair(PLAYER_COLORS[i]) | curses.A_BOLD

        # vertical divider between cards
        if i > 0:
            for row in range(1, rows - 1):
                try:
                    win.addch(row, x - 1, curses.ACS_VLINE, curses.color_pair(C_ACCENT))
                except curses.error:
                    pass

         # Flash: reverse video when this player just buzzed
        if flash_idx is not None and p.button_index == flash_idx:
            attr = attr | curses.A_REVERSE

        name = p.name[:card_w - 2]
        name_x = x + max(0, (card_w - len(name)) // 2)
        _addstr_safe(win, 2, name_x, name, attr)

        score_str = f"{p.score_display:g} pts"
        score_x = x + max(0, (card_w - len(score_str)) // 2)
        _addstr_safe(win, 3, score_x, score_str, curses.color_pair(C_DIM))

    # Bottom divider
    _hline(win, rows - 1, curses.ACS_HLINE)

    win.refresh()


# ── draw_main ─────────────────────────────────────────────────────────────────

def draw_main(win, game: GameState) -> None:
    win.erase()
    rows, cols = win.getmaxyx()

    # Status line (row 0)
    if game.phase == Phase.PREPARE:
        status = "[ PREPARE ]  Assign names, test buzzers (b1-b4), then type: start"
        attr   = curses.color_pair(C_P3) | curses.A_BOLD
    elif game.phase == Phase.QUIZ:
        status = f"[ QUIZ ]  Round {game.round_number}   |   next  /  end  /  <Name> +1  /  <Name> -1"
        attr   = curses.color_pair(C_SUCCESS) | curses.A_BOLD
    else:
        status = "[ FINISHED ]  See ranking in the log below."
        attr   = curses.color_pair(C_P4) | curses.A_BOLD

    _addstr_safe(win, 0, 2, status, attr)
    _hline(win, 1)

    # Buzz order (rows 3+)
    if game.buzzer_order:
        _addstr_safe(win, 3, 2, "Buzz order:", curses.A_BOLD)
        for i, idx in enumerate(game.buzzer_order):
            p     = game.player(idx)
            name  = p.name if p else f"Player {idx}"
            medal = MEDALS[min(i, len(MEDALS) - 1)]
            color = curses.color_pair(BUZZ_COLORS[min(i, len(BUZZ_COLORS) - 1)])
            row   = 4 + i
            if row >= rows:
                break
            _addstr_safe(win, row, 4, f"{medal}  {name}", color | curses.A_BOLD)
    elif game.phase == Phase.QUIZ:
        _addstr_safe(win, 3, 2, "Waiting for buzzers...", curses.color_pair(C_DIM) | curses.A_DIM)

    _hline(win, rows - 1)
    win.refresh()


# ── draw_log ──────────────────────────────────────────────────────────────────

def draw_log(win, messages: list[str]) -> None:
    win.erase()
    rows, cols = win.getmaxyx()
    capacity   = rows - 1   # leave bottom row for divider

    _addstr_safe(win, 0, 2, "Events", curses.color_pair(C_ACCENT) | curses.A_BOLD)

    visible = messages[-(capacity - 1):]
    for i, msg in enumerate(visible):
        row  = 1 + i
        prefix_attr = curses.color_pair(C_ACCENT) | curses.A_DIM
        text_attr   = curses.color_pair(C_DIM)
        _addstr_safe(win, row, 2, ">", prefix_attr)
        _addstr_safe(win, row, 4, msg, text_attr)

    _hline(win, rows - 1)
    win.refresh()


# ── draw_input ───────────────────────────────────────────────────────────────

def draw_input(win, buffer: list[str], hint: str = "") -> None:
    """Draw the current input buffer. Called every frame."""
    _, cols = win.getmaxyx()
    prompt = "> "
    win.erase()
    win.addstr(0, 0, prompt, curses.color_pair(C_INPUT) | curses.A_BOLD)

    text = "".join(buffer)
    win.addstr(0, len(prompt), text, curses.color_pair(C_DIM))

    if hint:
        trimmed = hint[:cols - len(prompt) - len(text) - 2]
        if trimmed:
            win.addstr(0, cols - len(trimmed) - 1,
                       trimmed, curses.color_pair(C_DIM) | curses.A_DIM)

    # Place the real cursor at end of typed text
    cursor_x = min(len(prompt) + len(buffer), cols - 1)
    try:
        curses.curs_set(1)
        win.move(0, cursor_x)
    except curses.error:
        pass

    win.refresh()
