# The Quizening

A curses-based CLI quiz buzzer tool. Runs entirely over SSH on a Raspberry Pi.
No MQTT, no second machine, no screenshare.

## Files

| File | Purpose |
|---|---|
| `main.py` | Entry point, main loop |
| `game.py` | Game state: phases, players, scoring, log |
| `commands.py` | Parse and execute host commands |
| `ui.py` | All curses drawing + input handling |
| `gpio_buzzer.py` | GPIO wiring (Pi only, silent no-op elsewhere) |

## Install & run

```bash
# No pip installs needed on a dev machine — curses is stdlib
python main.py

# On the Pi, install gpiozero if not already present:
# pip install gpiozero
```

## Commands

### PREPARE phase
| Command | Effect |
|---|---|
| `name 1 Alice` | Rename Button 1 to Alice |
| `b1` / `b2` / `b3` / `b4` | Simulate a buzzer press (dev/test mode) |
| `start` | Begin the quiz |

### QUIZ phase
| Command | Effect |
|---|---|
| `next` or `n` | Start the next round |
| `end` or `e` | End quiz and show ranking |
| `Alice +1` | Add a point to Alice |
| `Bob -1` | Remove a point from Bob |
| `b1–b4` | Still works as buzzer simulation |

## GPIO wiring

Default BCM pin assignments (edit `gpio_buzzer.py` to change):

| Button | GPIO (BCM) | LED (BCM) |
|---|---|---|
| Player 1 | 12 | 6 |
| Player 2 | 16 | 13 |
| Player 3 | 20 | 19 |
| Player 4 | 21 | 26 |

Buttons are `pull_up=True` — wire each button between the GPIO pin and GND.
