import network # import network library to work with Wi-Fi
import time # import time library
from machine import Pin # import only Pin library from machine module
import urequests # module for Rest API

# Wi-Fi connected status LED
# define and set default state
LED = Pin(16, Pin.OUT)
LED.value(0)

# Set Wi-Fi network to Station Interface
wlan = network.WLAN(network.STA_IF)
wlan.active(True) # enable Wi-Fi interface


# print Wi-Fi Scan of APs around
aps_scan = wlan.scan() # store last Wi-Fi AP scan
countAPs = len(aps_scan) # get number of APs found
for i in range(countAPs): # iterate over whole scan one-by-one
    print(aps_scan[i]) # print information about AP

# connect to predefined AP wlan.connect(SSID, Password)
#wlan.connect("LPWAN-IoT-XY", "LPWAN-IoT-XY-WiFi") # replace XY with your station number (correct 1 up to 10)
#wlan.connect("LPWAN-IoT-00", "LPWAN-IoT-00-WiFi") # example for teacher station with number 00
wlan.connect("xRD-03E9A5D5CA", "y5FrJ3?K6cFVM_tr")


# while Wi-Fi is not connected
while not wlan.isconnected():
    
    print("WIFI STATUS CONNECTED: " + str(wlan.isconnected())) # print current status aka False=Not connect, True=Connected
        
    time.sleep_ms(500) # check period set to 500 ms
    

LED.value(1) # set Wi-Fi status LED to High/On 

# after connection to Wi-Fi print current Wi-Fi configuration
print(wlan.ifconfig())

# send request to get names of astronauts in space right now
astronauts = urequests.get("http://api.open-notify.org/astros.json").json() # send Rest API request, then return response as json object

# print all astronaut names in cycle
number = astronauts['number']
for i in range(number):
    print(astronauts['people'][i]['name'])


# end of script