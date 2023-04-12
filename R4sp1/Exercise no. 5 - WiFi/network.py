import network # import network library to work with Wi-Fi
import time # import time library
from machine import Pin # import only Pin library from machine module
import usocket as socket # import usocket library as socket namespace, used for working with websockets

# Wi-Fi connected status LED
# define and set default state
LED = Pin(16, Pin.OUT)
LED.value(0)

# Set Wi-Fi network to Station Interface
wlan = network.WLAN(network.STA_IF)
wlan.active(True) # enable Wi-Fi interface


# print Wi-Fi Scan of APs around
#aps_scan = wlan.scan() # store last Wi-Fi AP scan
#countAPs = len(aps_scan) # get number of APs found
#for i in range(countAPs): # iterate over whole scan one-by-one
#    print(aps_scan[i]) # print information about AP

# connect to predefined AP wlan.connect(SSID, Password)
#wlan.connect("LPWAN-IoT-XY", "LPWAN-IoT-XY-WiFi") # replace XY with your station number (correct 1 up to 10)
wlan.connect("LPWAN-IoT-08", "LPWAN-IoT-08-WiFi") # example for teacher station with number 00

# while Wi-Fi is not connected
while not wlan.isconnected():
    
    print("WIFI STATUS CONNECTED: " + str(wlan.isconnected())) # print current status aka False=Not connect, True=Connected
        
    time.sleep_ms(500) # check period set to 500 ms
    

LED.value(1) # set Wi-Fi status LED to High/On 

# after connection to Wi-Fi print current Wi-Fi configuration
print(wlan.ifconfig())

# TCP/UDP usocket
# https://docs.micropython.org/en/v1.14/library/usocket.html

#UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # create socket SOCK_DGRAM means UDP socket
#addr = socket.getaddrinfo('192.168.137.1', 1111)[0][-1] # translates all necessary input arguments into workable format for socket functions
sock.settimeout(20) # set socket response timeout to 5 second, if no message comes then socket automatically closes

sock.sendto("BBCexp7hquWYnAd53vXjd7ytqqXVATxia7Do0dGTMtMoDjdxaAgjHOOe53MAZlDObOV0fXbG4sBNWlJPQyBUcrRHo8sj3NVq6Th6jDw1O0Mdmid3Qz6d8EJO8tSqWzLn", ('192.168.137.1', 1111))

try:
    #sock.bind(('192.168.137.1', 1111))
    data,addr=sock.recvfrom(1024)
    print("received message: %s" % data)
except:
    print("Error")

print("End of script")
# end of script