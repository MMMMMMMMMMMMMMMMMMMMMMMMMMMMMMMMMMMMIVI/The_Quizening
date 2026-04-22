"""
GPIO buzzer integration (Raspberry Pi only).

Wraps gpiozero so that physical button presses get safely posted into
game.buzz_queue, which the main loop drains on every iteration.

Usage:
    from gpio_buzzer import setup_gpio, teardown_gpio
    setup_gpio(game)           # call once at startup
    # ... main loop reads game.buzz_queue as usual ...
    teardown_gpio()            # call on exit (optional; gpiozero cleans up)

If gpiozero is not available (running on a dev machine) this module does
nothing and setup_gpio() is a no-op — buzzer simulation via b1-b4 commands
still works in that case.
"""
from __future__ import annotations
from game import GameState
import threading

_buttons = []   # keep references alive so gpiozero doesn't GC them

BUZZER_PINS = [26, 16, 20, 21]   # BCM pin numbers, one per player
LED_PINS    = [18,  13, 19, 12]   # matching LEDs (one per buzzer)
TONE_PIN = 23
PLAYER_TONES = {1: 523, 2: 659, 3: 784, 4: 988,}# C5 E5 G5 B5


def setup_gpio(game: GameState) -> bool:
    """
    Register gpiozero callbacks. Returns True on success, False if gpiozero
    is unavailable (non-Pi environment).
    """
    global _buttons
    try:
        from gpiozero import Button, PWMLED, TonalBuzzer
    except Exception:
        return False

    leds = [PWMLED(pin) for pin in LED_PINS]
    buzz = TonalBuzzer(TONE_PIN)

    for i, pin in enumerate(BUZZER_PINS):
        btn = Button(pin, pull_up=True)
        player_index = i + 1   # 1-based

        def make_press_cb(idx, led, bzr):
            def on_press():
                game.buzz_queue.put(idx)   # thread-safe
                beep(bzr, frequency=PLAYER_TONES[idx], duration=0.15)
                led.blink(on_time=0.1, off_time=0.1, n=3)
            return on_press

        btn.when_pressed  = make_press_cb(player_index, leds[i], buzz)
        _buttons.append(btn)

    return True


def teardown_gpio() -> None:
    """Release all gpiozero resources."""
    for btn in _buttons:
        btn.close()
    _buttons.clear()


def beep(buzzer, frequency=440, duration=0.15):
    def _run():
        buzzer.play(frequency)
        threading.Event().wait(duration)
        buzzer.stop()
    threading.Thread(target=_run, daemon=True).start()