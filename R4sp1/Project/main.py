import  machine
import time
from lora_E5 import LoRaE5
from PiicoDev_LIS3DH import PiicoDev_LIS3DH
from PiicoDev_Unified import sleep_ms

cycle = 4500
last_time_but = 0
last_time_LoRa = time.ticks_ms()


motion = PiicoDev_LIS3DH() # Initialise the accelerometer
motion.range = 2 # Set the range to +-2g

gpsModule = machine.UART(0, baudrate=9600)

buff = bytearray(255)

TIMEOUT = False
FIX_STATUS = False

latitude = ""
longitude = ""
satellites = ""
GPStime = ""

last_time_but = 0
last_time_acc = 0
last_time_main = 0

last_ax = 0
last_ay =0
last_az = 0


print("Setup - Start")

button = machine.Pin(21, machine.Pin.IN)
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
lora.set_port(55)
lora.set_counters(cycle, cycle)
time.sleep(2)

print("Setup - End")


def getGPS(gpsModule):
    global FIX_STATUS, TIMEOUT, latitude, longitude, satellites, GPStime

    timeout = time.ticks_ms() + 10000
    while True:
        gpsModule.readline()
        buff = str(gpsModule.readline())
        parts = buff.split(',')
        print(buff)

        if (parts[0] == "b'$GNGLL" and len(parts) == 8):
            if (parts[1] and parts[2] and parts[3] and parts[4] and parts[5] and parts[6] and parts[7]):
                print(buff)

                longitude = convertToDegree(parts[1])
                if (parts[2] == 'S'):
                    longitude = -longitude
                latitude = convertToDegree(parts[3])
                if (parts[4] == 'W'):
                    latitude = -latitude
                FIX_STATUS = True
                break

        if (time.ticks_ms() > timeout):
            TIMEOUT = True
            break
        time.sleep_ms(500)
        
        
def convertToDegree(RawDegrees):
    RawAsFloat = float(RawDegrees)
    firstdigits = int(RawAsFloat / 100)
    nexttwodigits = RawAsFloat - float(firstdigits * 100)

    Converted = float(firstdigits + nexttwodigits / 60.0)
    Converted = '{0:.6f}'.format(Converted)
    return str(Converted)

def button_pressed_handler(pin):
    global last_time_but
    new_time_but = time.ticks_ms()
    # if it has been more that 1/5 of a second since the last event, we have a new event
    if (new_time_but - last_time_but) > 200: 
        fun()
        last_time_but = new_time_but
        
button.irq(trigger=machine.Pin.IRQ_FALLING, handler = button_pressed_handler)

def fun():
    global cycle, FIX_STATUS, longitude, latitude, satellites, GPStime, TIMEOUT
    getGPS(gpsModule)
    if (FIX_STATUS == True):
        print("Printing GPS data...")
        print(" ")
        print("Latitude: " + latitude)
        print("Longitude: " + longitude)
        print("----------------------")
        cycle += 5
        lora.set_counters(cycle, cycle)
        time.sleep(2)
        print("LoRa cycle: " + str(cycle))
        lora.send_ascii(str(latitude) + "b" + str(longitude))
        time.sleep(10)
        lora.check_link()
        time.sleep(10)
        
    FIX_STATUS = False
    
    if (TIMEOUT == True):
        print("No GPS data is found.")
        cycle += 5
        lora.set_counters(cycle, cycle)
        time.sleep(2)
        print("LoRa cycle: " + str(cycle))
        lora.send_ascii("0b0")
        time.sleep(10)
        lora.check_link()
        time.sleep(10)
        TIMEOUT = False
    
while True:
    x, y, z = motion.acceleration
    new_ax=round(x,2)
    new_ay=round(y,2)
    new_az=round(z,2)
    
    if new_ax != last_ax or new_ay != last_ay or new_az != last_az:
        new_time_acc = time.ticks_ms()
        if last_time_acc == 0:
            new_time_acc += 55000
        if (new_time_acc - last_time_acc) > 60000:
            print("Acc send")
            print(new_ax, new_ay, new_az)
            fun()
            last_time_main = time.ticks_ms()
            if last_time_main == 0:
                last_time_acc = (new_time_acc - 55000)    
            last_time_acc = new_time_acc
        last_ax = new_ax
        last_ay = new_ay
        last_az = new_az
        
    new_time_main = time.ticks_ms()
    if (new_time_main - last_time_main) > 120000:
        print("Timed send")
        fun()
        last_time_main = new_time_main