from machine import Pin
import time
from lora_E5 import LoRaE5


print("Setup - Start")
led = Pin(15, Pin.OUT)

lora = LoRaE5(tx_pin=4, rx_pin=5, speed=9600)


lora.set_id('DevEui', '70B3D57ED004DF1B')
lora.set_id('DevAddr', '260112FD')

lora.set_key('NWKSKEY', '4CC307EDD9964CC9B0A1E529130A15D5')
lora.set_key('APPSKEY', 'C66614E4EFFAF253ADE923A96CFA8147')

time.sleep(2)

lora.set_dr_band('EU868')
lora.set_mode('LWABP')

time.sleep(2)

lora.set_power(12)
time.sleep(2)


#lora.set_etsi_duty_cycle(True)
lora.set_duty_cycle(1)
time.sleep(2)


time.sleep(2)
lora.set_port(55)
cycle = 1420
lora.set_counters(cycle, cycle)


time.sleep(5)
lora.send_ascii("A")
time.sleep(15)


print("Setup - End")


while True:
    cycle += 5
    print("While cycle: " + str(cycle))
    lora.send_ascii(str(cycle))
    time.sleep(10)
    lora.check_link()
    time.sleep(10)