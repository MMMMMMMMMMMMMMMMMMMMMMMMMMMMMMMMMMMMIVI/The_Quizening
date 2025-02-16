from gpiozero import Button, LED
import paho.mqtt.client as mqtt
from signal import pause
from time import sleep

client = mqtt.Client(client_id="raspberrypi", protocol=mqtt.MQTTv311)
client.connect("localhost", 1883, 60)

BUZZER_PINS = [12, 16, 20, 21]
LED_PINS = [6, 13, 19, 26]
buzzers = [Button(pin, pull_up=True) for pin in BUZZER_PINS]
leds = [LED(pin) for pin in LED_PINS]

def buzzer_pressed(buzzer_index):
    print(f"Buzzer {buzzer_index + 1} gedrückt!")
    client.publish("buzzer/pressed", f"{buzzer_index + 1}")
    leds[buzzer_index].on()

for i, buzzer in enumerate(buzzers):
    buzzer.when_pressed = lambda i=i: buzzer_pressed(i)
    buzzer.when_released = lambda i=i: leds[i].off()
    sleep(0.1)

try:
    client.loop_start()
    pause()
except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()