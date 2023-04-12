from network import WLAN
from machine import Pin, I2C
import network
import machine
import time
import ujson
import ahtx0
# if you have error importing, check that you copied all coap library files into pico filesystem
# (coap_macros, coap_option, coap_packet, coap_reader, coap_writer, microcoapy)
import microcoapy
import coap_macros


#CoAP server key information
_SERVER_IP ='86.49.182.194'
_SERVER_PORT = 36105  #5683 36105 default CoAP port
_COAP_POST_URL = 'api/v1/IoT_06/telemetry' # fill your Device name, select based on your workstation
_COAP_GET_REQ_URL = 'api/v1/IoT_06/attributes' # fill your Device name, select based on your workstation
_COAP_PUT_REQ_URL = 'led/turnOn'
_COAP_AUT_PASS = 'authorization=IoT_06' # fill your Device name, select based on your workstation


"""
************************************
    Student: fill definitions
************************************
"""
#Configure pinout
LED = machine.Pin(15, machine.Pin.OUT)
LED2 = machine.Pin(16, machine.Pin.OUT)
BUTTON1 = machine.Pin(20, machine.Pin.IN)
BUTTON2 = machine.Pin(21, machine.Pin.IN)
BUTTON3 = machine.Pin(22, machine.Pin.IN)
LED.value(0)
LED2.value(0)

#Coap POST Message function.
def sendPostRequest(client, json):
    messageId = client.post(_SERVER_IP, _SERVER_PORT, _COAP_POST_URL, json,
                                   None, coap_macros.COAP_CONTENT_FORMAT.COAP_APPLICATION_JSON)
    print("[POST] Message Id: ", messageId)


#Coap PUT Message function.
def sendPutRequest(client):
    messageId = client.put(_SERVER_IP, _SERVER_PORT, _COAP_PUT_REQ_URL, "test",
                                   _COAP_AUT_PASS,
                                   coap_macros.COAP_CONTENT_FORMAT.COAP_TEXT_PLAIN)
    print("[PUT] Message Id: ", messageId)


#Coap GET Message function.
def sendGetRequest(client):
    messageId = client.get(_SERVER_IP, _SERVER_PORT, _COAP_GET_REQ_URL)
    print("[GET] Message Id: ", messageId)

#On message callback. Called each time when message that is not ACK is received.
def receivedMessageCallback(packet, sender):
    print('Message received:', packet.toString(), ', from: ', sender)
    print('Packet info received:', packet.messageid, ', from: ', sender)
    #Process the message content here. TODO

#Creates JSON from the available peripherals
def createJSON():
    json_string={"temperature":tmp_sensor.temperature(),"20":BUTTON1.value()!=True,"21":BUTTON2.value()!=True,"22":BUTTON3.value()!=True}
    json = ujson.dumps(json_string)
    return json

#Main program----------------------------------------------------


#Initialize temperature sensor via I2C interface
i2c1 = I2C(1, scl = Pin(3), sda = Pin(2), freq = 400000)
tmp_sensor = ahtx0.AHT10(i2c1)
tmp_sensor.initialize()

#Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("LPWAN-IoT-06", "LPWAN-IoT-06-WiFi")


#Create a CoAP client
client = microcoapy.Coap()
client.debug = True

#Set the callback function for the message reception
client.responseCallback = receivedMessageCallback

# Starting CoAP client
client.start()

#Time variables and period definition
ticks_start = time.ticks_ms()
get_ticks_start = time.ticks_ms()
get_period = 6500
send_period = 15000#ms

#Send get request to get the initial state of the LED
sendGetRequest(client)

#Infinite loop.
while(1):
    #If it is time to send data, create JSON and send it to the server
    if (time.ticks_diff(time.ticks_ms(), ticks_start) >= send_period):
        ticks_start=time.ticks_ms()
        json = createJSON()
        sendPostRequest(client, json)
      
    #Get the LED state from the server periodically
    if (time.ticks_diff(time.ticks_ms(), get_ticks_start) >= get_period):
        get_ticks_start = time.ticks_ms()
        sendGetRequest(client)
    
    #Let the client do it's thing - send and receive CoAP messages.
    client.poll(10000, pollPeriodMs=1)
   
#Stop the client --- Should never get here.
client.stop()
