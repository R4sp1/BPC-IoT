import machine
import neopixel
import time
import random

# set-up Neopixel WS2812B on pin 28, 1 RGB LED present
np = neopixel.NeoPixel(machine.Pin(28), 1)

# set-up LED on pin 16 (build-in LED on GP25 is controlled by Wi-Fi module, not RP2040 MCU on Pico W variant)
LED = machine.Pin(7, machine.Pin.OUT)

# set-up PWM channel for Buzzer on pin 16
led_pwm = machine.PWM(machine.Pin(16))

# set led frequency to 1000 Hz = 1 kHz
led_pwm.freq(5)


# set-up 3 used buttons (from left to right)
user_button_1 = machine.Pin(20, machine.Pin.IN)
user_button_2 = machine.Pin(21, machine.Pin.IN)
user_button_3 = machine.Pin(22, machine.Pin.IN)