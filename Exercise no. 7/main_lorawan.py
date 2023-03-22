from machine import Pin
import time
from lora_E5 import LoRaE5


print("Setup - Start")
led = Pin(15, Pin.OUT)

lora = LoRaE5(tx_pin=4, rx_pin=5, speed=9600)

lora.test_at()
lora.get_id()

# lora.set_id('DevAddr', '260112FD')
# lora.get_version()
# lora.send_ascii("Test", False)
# lora.set_port(128)
# lora.get_port()
# lora.get_adr()
# lora.set_adr(False)
# lora.get_dr()
# lora.set_dr(5)
# lora.get_band_scheme()
# lora.get_all_channels()
# lora.get_channel(2)
# lora.get_enabled_channels()
# lora.get_power()
# lora.set_power(10)
# lora.get_power_map()
# lora.get_ret_limit()
# lora.get_rx2()
# lora.set_rx2(869525000, 5)
lora.set_rx2(869525000, 5)
lora.enable_channel(0)
lora.enable_channel(1)
lora.enable_channel(2)
lora.enable_channel(3)
lora.enable_channel(4)
lora.enable_channel(5)
lora.enable_channel(6)
lora.enable_channel(7)

lora.set_id('DevEui', '70B3D57ED004DF1B')
lora.set_id('DevAddr', '260112FD')

lora.set_key('NWKSKEY', '4CC307EDD9964CC9B0A1E529130A15D5')
lora.set_key('APPSKEY', 'C66614E4EFFAF253ADE923A96CFA8147')

lora.set_dr_band('EU868')
lora.set_mode('LWABP')
lora.set_dr(5)



# lora.set_channel(0,868100000,0,5)
# lora.set_channel(1,868300000,0,5)
# lora.set_channel(2,868500000,0,5)
# lora.set_channel(3,867100000,0,5)
# lora.set_channel(4,867300000,0,5)
# lora.set_channel(5,867500000,0,5)
# lora.set_channel(6,867700000,0,5)
# lora.set_channel(7,867900000,0,5)



# lora.set_etsi_duty_cycle(True)
lora.set_duty_cycle(4)

lora.set_power(12)

lora.get_enabled_channels()
lora.set_port(55)
lora.set_counters(33, 3)



lora.send_ascii('Hello')
lora.read_n_times(25)
# 
# lora.get_rx_delay()
# lora.set_rx_delay('RX1', 1000)

print("Setup - End")

cycle = 0
while True:
    print("While cycle: " + str(cycle))
    lora.check_link()    
    cycle += 1
    time.sleep(10)
