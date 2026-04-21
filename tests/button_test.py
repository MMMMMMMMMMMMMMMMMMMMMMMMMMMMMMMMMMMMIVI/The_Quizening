from gpiozero import Button, PWMLED
from signal import pause
from time import sleep

red_button = Button(26)
red_led = PWMLED(18)

green_button = Button(16)
green_led = PWMLED(13)

blue_button = Button(20)
blue_led = PWMLED(19)

yellow_button = Button(21)
yellow_led = LED(12)
    
red_button.when_pressed = red_led.on
red_button.when_released = red_led.off

green_button.when_pressed = green_led.on
green_button.when_released = green_led.off

blue_button.when_pressed = blue_led.on
blue_button.when_released = blue_led.off

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