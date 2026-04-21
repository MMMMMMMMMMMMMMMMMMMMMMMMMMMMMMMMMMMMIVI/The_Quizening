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

_buttons = []   # keep references alive so gpiozero doesn't GC them

BUZZER_PINS = [12, 16, 20, 21]   # BCM pin numbers, one per player
LED_PINS    = [6,  13, 19, 26]   # matching LEDs (one per buzzer)


def setup_gpio(game: GameState) -> bool:
    """
    Register gpiozero callbacks. Returns True on success, False if gpiozero
    is unavailable (non-Pi environment).
    """
    global _buttons
    try:
        from gpiozero import Button, LED
    except Exception:
        return False

    leds = [LED(pin) for pin in LED_PINS]

    for i, pin in enumerate(BUZZER_PINS):
        btn = Button(pin, pull_up=True)
        player_index = i + 1   # 1-based

        def make_press_cb(idx, led):
            def on_press():
                game.buzz_queue.put(idx)   # thread-safe
                led.on()
            return on_press

        def make_release_cb(led):
            def on_release():
                led.off()
            return on_release

        btn.when_pressed  = make_press_cb(player_index, leds[i])
        btn.when_released = make_release_cb(leds[i])
        _buttons.append(btn)

    return True


def teardown_gpio() -> None:
    """Release all gpiozero resources."""
    for btn in _buttons:
        btn.close()
    _buttons.clear()
