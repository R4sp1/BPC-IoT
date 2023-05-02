from machine import Pin, UART, I2C
import time
from lora_E5 import LoRaE5
import utime
from micropython import const
import ahtx0


print("Setup - Start")
led = Pin(15, Pin.OUT)
BUTTON1 = Pin(20, Pin.IN)

lora = LoRaE5(tx_pin=4, rx_pin=5, speed=9600)
#GPS = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
gps_module = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))


#Store GPS Coordinates
latitude = ""
longitude = ""
satellites = ""
gpsTime = ""

#function to get gps Coordinates
def getPositionData(gps_module):
    global FIX_STATUS, TIMEOUT, latitude, longitude, satellites, gpsTime
    
    #run while loop to get gps data
    #or terminate while loop after 5 seconds timeout
    timeout = time.time() + 8   # 8 seconds from now
    while True:
        gps_module.readline()
        buff = str(gps_module.readline())

        parts = buff.split(',')
        
        #if no gps displayed remove "and len(parts) == 15" from below if condition
        if (parts[0] == "b'$GNGGA" and len(parts) == 15):
            if(parts[1] and parts[2] and parts[3] and parts[4] and parts[5] and parts[6] and parts[7]):
                print(buff)
                """
                print("Message ID  : " + parts[0])
                print("UTC time    : " + parts[1])
                print("Latitude    : " + parts[2])
                print("N/S         : " + parts[3])
                print("Longitude   : " + parts[4])
                print("E/W         : " + parts[5])
                print("Position Fix: " + parts[6])
                print("n sat       : " + parts[7])
                """
                latitude = convertToDigree(parts[2])
                # parts[3] contain 'N' or 'S'
                if (parts[3] == 'S'):
                    latitude = -latitude
                longitude = convertToDigree(parts[4])
                # parts[5] contain 'E' or 'W'
                if (parts[5] == 'W'):
                    longitude = -longitude
                satellites = parts[7]
                gpsTime = parts[1][0:2] + ":" + parts[1][2:4] + ":" + parts[1][4:6]
                FIX_STATUS = True
                break
        else:
            TIMEOUT = False
            FIX_STATUS = True
        if (time.time() > timeout):
            TIMEOUT = True
            break
        utime.sleep_ms(500)

def convertToDigree(RawDegrees):

    RawAsFloat = float(RawDegrees)
    firstdigits = int(RawAsFloat/100) #degrees
    nexttwodigits = RawAsFloat - float(firstdigits*100) #minutes
    
    Converted = float(firstdigits + nexttwodigits/60.0)
    Converted = '{0:.6f}'.format(Converted) # to 6 decimal places
    return str(Converted)
lora.set_dr(5)
lora.set_power(10)
lora.set_id('DevEui', '70B3D57ED004E4E1')
lora.set_id('DevAddr', '260B990D')

lora.set_key('NWKSKEY', '8E17FA1F9E8A46962748541B02478824')
lora.set_key('APPSKEY', '5FB765E8CA11F8FAFFADDC57D043EFA4')

lora.set_dr_band('EU868')
lora.set_mode('LWABP')
lora.set_port(55)

lora.set_etsi_duty_cycle(False)

a=7420

lora.set_counters(a, a)
lora.check_link()
cycle = 1

def pinPressedCallback(pin):
    global client
    time.sleep(0.1)
    global cycle
    print("Button Pressed. " + str(pin))
    lora.set_counters(a + cycle, 0)
    latitude=49.227009
    longitude=16.574512
    msg=str(latitude)+"a"+str(longitude)
    lora.send_ascii(msg)
    lora.check_link()
    print("nejsem zaseklý")
    cycle += 1

    
BUTTON1.irq(trigger=Pin.IRQ_FALLING, handler=pinPressedCallback)


while False:
    print("While cycle: " + str(cycle))
    lora.set_counters(1780 + cycle, 0)
    msg='AAAA'+str(cycle)
    lora.send_ascii(msg)
    cycle += 1
    time.sleep(10)

while True:
    
    getPositionData(gps_module)
    if(FIX_STATUS == True):
        print("fix......")
        
        print(latitude)
        print(longitude)
        print(satellites)
        print(gpsTime)
        
    FIX_STATUS = False
        
    if(TIMEOUT == True):
        print("Request Timeout: No GPS data is found.")
        TIMEOUT = False

        
    lora.set_counters(a + cycle, 0)
    latitude=49.227009
    longitude=16.574512
    msg=str(latitude)+"a"+str(longitude)
    lora.send_ascii(msg)
    print("nejsem zaseklý")
    
    cycle += 1

    time.sleep(70)    
        
