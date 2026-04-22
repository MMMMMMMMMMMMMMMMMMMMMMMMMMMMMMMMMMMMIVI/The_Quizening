from gpiozero import Button, PWMLED, TonalBuzzer
from signal import pause
from time import sleep
from gpiozero.tones import Tone

b = TonalBuzzer(23)

def blicki(led):
    def _run():
        for _ in range(3):
            led.on()
            sleep(0.1)
            led.off()
            sleep(0.1)
    return _run

red_button = Button(26)
red_led = PWMLED(18)

green_button = Button(16)
green_led = PWMLED(13)

blue_button = Button(20)
blue_led = PWMLED(19)

yellow_button = Button(21)
yellow_led = PWMLED(12)

red_button.when_pressed = lambda:[red_led.on, blue_led.on]
red_button.when_released = lambda:[red_led.off, blue_led.off]

green_button.when_pressed = green_led.on
green_button.when_released = green_led.off

blue_button.when_pressed = blicki(blue_led)

yellow_button.when_pressed = yellow_led.on
yellow_button.when_released = yellow_led.off

"""while True:
    yellow_led.on()
    sleep(0.05)
    red_led.off()
    sleep(0.05)
    blue_led.on()
    sleep(0.05)
    yellow_led.off()
    sleep(0.05)
    green_led.on()
    sleep(0.05)
    blue_led.off()
    sleep(0.05)
    red_led.on()
    sleep(0.05)
    green_led.off()
    sleep(0.05)"""

pause()
