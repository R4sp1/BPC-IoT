from machine import Pin, I2C
import time
import random
import ahtx0

LED16  = machine.Pin(16, machine.Pin.OUT)
LED15  = machine.Pin(15, machine.Pin.OUT)

BUT20 = Pin(20, Pin.IN)

i2c = I2C(id=1, scl=Pin(3), sda=Pin(2), freq=400_000)

print(i2c.scan())
time.sleep_ms(50)
sensor = ahtx0.AHT20(i2c)
time.sleep_ms(50)

led_last_changed = time.ticks_ms()

sensor_last_changed = time.ticks_ms()

sensor_timer = 5000

led_timer = 250

#while True:
    #


while True:
    
    if time.ticks_diff(time.ticks_ms(), sensor_last_changed) >= sensor_timer:
        sensor_last_changed = time.ticks_ms()
        print("\nTemperature: %0.2f C" % sensor.temperature)
        print("Humidity: %0.2f %%" % sensor.relative_humidity)
    
    if time.ticks_diff(time.ticks_ms(), led_last_changed) >= led_timer:
        led_last_changed = time.ticks_ms() #store the last LED change timestamp
        LED15.toggle()
    if BUT20.value():
        LED16.value(0)	#LED OFF
    else:
        LED16.value(1)
    
    
# 