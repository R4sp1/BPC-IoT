import machine
import neopixel
import time
import random

LED7 = machine.Pin(7, machine.Pin.OUT)
LED16  = machine.Pin(16, machine.Pin.OUT)
LED15  = machine.Pin(15, machine.Pin.OUT)

BUT20 = machine.Pin(20, machine.Pin.IN)
BUT21 = machine.Pin(21, machine.Pin.IN)
BUT22 = machine.Pin(22, machine.Pin.IN)

BUT21_pr = False
BUT22_pr = False
x = 1
        
        
def handle_interrupt(pin):
    global BUT21_pr
    global BUT222_pr
    global x
    if pin == BUT20:
        if x == 1:
            LED16.value(1)
            x = 0
        else:
            LED16.value(0)
            x = 1
        
BUT20.irq(trigger=machine.Pin.IRQ_FALLING, handler = handle_interrupt)

while(1):
    LED7.value(1)
    time.sleep_ms(1000)
    LED7.value(0)
    time.sleep_ms(1000)
    while(BUT21.value() == 0 and BUT22.value() == 0):
        LED15.value(1)
    LED15.value(0)
        