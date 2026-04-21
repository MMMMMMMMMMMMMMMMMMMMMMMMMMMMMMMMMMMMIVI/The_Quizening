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
from ui       import init_colors, create_windows, draw_scores, draw_main, draw_log, get_command
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
        while True:
            win_scores, win_main, win_log, win_input = wins

            # Drain any buzzer presses that arrived via GPIO while we were blocked
            while True:
                try:
                    idx = game.buzz_queue.get_nowait()
                    game.register_buzz(idx)
                except queue.Empty:
                    break

            # Redraw everything
            draw_scores(win_scores, game.players)
            draw_main(win_main, game)
            draw_log(win_log, game.last_log(7))

            # Block on input
            cmd = get_command(win_input, hint=_HINTS[game.phase])

            # Handle resize sentinel
            if cmd == "\x00RESIZE":
                stdscr.clear()
                stdscr.refresh()
                wins = create_windows(stdscr)
                continue

            # Process command
            process(game, cmd)

            # Exit after the end screen has been drawn once
            if game.phase == Phase.END:
                # Redraw one final time so the ranking is visible
                draw_scores(win_scores, game.players)
                draw_main(win_main, game)
                draw_log(win_log, game.last_log(7))
                win_input.erase()
                win_input.addstr(0, 0, "  Press any key to exit...")
                win_input.refresh()
                win_input.getch()
                break

    finally:
        teardown_gpio()


if __name__ == "__main__":
    curses.wrapper(main)
