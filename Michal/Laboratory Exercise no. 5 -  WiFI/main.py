import machine
import neopixel
import time
import random
from machine import Pin, PWM

# set-up Neopixel WS2812B on pin 28, 1 RGB LED present
np = neopixel.NeoPixel(machine.Pin(28), 1)

# set-up LED on pin 16 (build-in LED on GP25 is controlled by Wi-Fi module, not RP2040 MCU on Pico W variant)
LED = machine.Pin(16, machine.Pin.OUT)
LED16 = machine.Pin(16, machine.Pin.OUT)
LED18 = machine.Pin(19, machine.Pin.OUT)

# set-up PWM channel for Buzzer on pin 18
buzzer_pwm = machine.PWM(machine.Pin(13))
# set PWM frequency to 1000 Hz = 1 kHz
buzzer_pwm.freq(100)

# set-up 3 used buttons (from left to right)
user_button_1 = machine.Pin(20, machine.Pin.IN)
user_button_2 = machine.Pin(21, machine.Pin.IN)
user_button_3 = machine.Pin(22, machine.Pin.IN)


#LED 10
LED_BUITLTIN = 15 # For Raspberry Pi Pico

pwm_led = PWM(Pin(LED_BUITLTIN, mode=Pin.OUT)) # Attach PWM object on the LED pin
pwm_led.freq(8)

duty_cycle = 50 # Between 0 - 100 %
pwm_led.duty_u16(int((duty_cycle/100)*65_535))






# define initial values for all output devices
# set LED to off state
LED.value(0)
#LED18.value(1)
# set RGB LED to off state
red = 0
green = 0
blue = 0
brightness = 0

# write data to first Neopixel LED (array starts from 0 index)
np[0] = (red, green, blue, brightness)
np.write()

# flag to enable/disable RGB
enable_RGB = False

# set flag to False, button was not pressed initialy
button_pressed = False
button_pressedLED = False

# ****** GPIO interrupt handler function ******
def handle_interrupt(pin):
    # global variable/flag indicating press of precific button
    global button_pressed
    
    # check if pressed button is expected button
    if pin == user_button_3:
        # change state of flag to True/press detected
        button_pressed = True
    # handle wrong button press
    else:
        print("Not right button")
        print(pin)
    
    global button_pressedLED
    if pin == user_button_1:
        # change state of flag to True/press detected
        button_pressed = True
    # handle wrong button press
    else:
        print("Not right button")
        print(pin)
# create simple interrupt handling for pressing button
user_button_3.irq(trigger=machine.Pin.IRQ_FALLING, handler = handle_interrupt)

# infinite while cycle = NEVER ENDS
while(1):
    
    # check if button_pressed flag is true, then do action, then clear flag
    if button_pressed:
        print("Button pressed")
        
        # RED
        np[0] = (255, 0, 0, 0) # Red, green, blue, brightness
        np.write()
        time.sleep_ms(500)
        
        # GREEN
        np[0] = (0, 255, 0, 0) # Red, green, blue, brightness
        np.write()
        time.sleep_ms(500)
        
        # BLUE
        np[0] = (0, 0, 255, 0) # Red, green, blue, brightness
        np.write()
        time.sleep_ms(500)
        
        # WHITE
        np[0] = (255, 255, 255, 0) # Red, green, blue, brightness
        np.write()
        time.sleep_ms(500)
        
        # ALL OFF
        np[0] = (0, 0, 0, 0) # Red, green, blue, brightness
        np.write()
        time.sleep_ms(500)
        
        # clear status flag in the end
        button_pressed = False
        
    
    # check if user enables Buzzer
    # indicated by LED
    if user_button_1.value() == 0:
        buzzer_pwm.duty_u16(2)
        LED.value(1)
        print("BUZZER: ON")
    else:
        LED.value(0)
        buzzer_pwm.duty_u16(0)
    
    if button_pressedLED:
        LED16.value(1)
   
    # check if user wants to enable/disable RGB random color generator
    if user_button_2.value() == 0:
        # toggle/change state of enable_RGB flag
        enable_RGB = not enable_RGB
    
    # generate random RGB color
    if enable_RGB:
        # generate random values for RGB color LEDs
        red = random.randrange(0,255, 16)
        green = random.randrange(0,255, 16)
        blue = random.randrange(0,255, 16)
        brightness = random.randrange(64,128, 1)
        
            
        print("RGB: {}-{}-{}-{}".format(red, green, blue, brightness))
        
        # set and write color set to RGB LED on position 0 (first on the bus)
        np[0] = (red, green, blue, brightness) # Red, green, blue, brightness
        np.write()
    else:
        # set RGB LED to off state
        red = 0
        green = 0
        blue = 0
        brightness = 0

        # write data to first Neopixel LED (array starts from 0 index)
        np[0] = (red, green, blue, brightness)
        np.write()

    # sleep defined time
    time.sleep_ms(250)