#!/usr/bin/env python3
"""
The Quizening — entry point.

Run on your Pi:
    python main.py

Run on a dev machine (no GPIO):
    python main.py
    # use b1–b4 commands to simulate buzzer presses
"""
import curses
import queue

from game     import GameState, Phase
from ui       import init_colors, create_windows, draw_scores, draw_main, draw_log, draw_input
from commands import process
from gpio_buzzer import setup_gpio, teardown_gpio

# Hint text shown right-aligned in the input bar
_HINTS = {
    Phase.PREPARE: "name <1-4> <Name>  |  b1-b4  |  start",
    Phase.QUIZ:    "<Name> +1  |  <Name> -1  |  next  |  end",
    Phase.END:     "(quiz over)",
}


def main(stdscr) -> None:
    curses.curs_set(0)
    stdscr.clear()

    init_colors()
    game = GameState()

    # GPIO setup — silent no-op if gpiozero isn't available
    gpio_ok = setup_gpio(game)
    if gpio_ok:
        game.log("GPIO ready. Physical buzzers active.")
    else:
        game.log("No GPIO detected — use b1-b4 to simulate buzzers.")

    game.log("Welcome! Assign player names, then type 'start'.")

    wins = create_windows(stdscr)   # (win_scores, win_main, win_log, win_input)

    try:
        input_buf = [] 

        while True:
            win_scores, win_main, win_log, win_input = wins

            # Drain any buzzer presses that arrived via GPIO while we were blocked
            changed = False
            while True:
                try:
                    idx = game.buzz_queue.get_nowait()
                    game.register_buzz(idx)
                    game.last_flash = idx          # new field, see game.py
                    changed = True
                except queue.Empty:
                    break

            # Redraw if something changed or first frame
            draw_scores(win_scores, game.players, game.last_flash)
            draw_main(win_main, game)
            draw_log(win_log, game.last_log(20))
            draw_input(win_input, input_buf, _HINTS[game.phase])

            # Non-blocking getch (timeout set in create_windows)
            ch = win_input.getch()

            if ch == curses.KEY_RESIZE:
                stdscr.clear()
                stdscr.refresh()
                wins = create_windows(stdscr)
                input_buf = []
                continue

            elif ch in (curses.KEY_ENTER, 10, 13):
                cmd = "".join(input_buf).strip()
                input_buf = []
                if game.last_flash is not None:
                    game.last_flash = None
                process(game, cmd)
                if game.phase == Phase.END:
                    draw_scores(win_scores, game.players, None)
                    draw_main(win_main, game)
                    draw_log(win_log, game.last_log(20))
                    win_input.erase()
                    win_input.addstr(0, 0, "  Press any key to exit...")
                    win_input.refresh()
                    win_input.getch()
                    break

            elif ch in (curses.KEY_BACKSPACE, 127, 8):
                if input_buf:
                    input_buf.pop()

            elif ch != -1 and 32 <= ch <= 126:
                input_buf.append(chr(ch))

    finally:
        teardown_gpio()


if __name__ == "__main__":
    curses.wrapper(main)
