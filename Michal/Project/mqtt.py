import network
import time
import urequests
from machine import Pin, I2C
import usocket as socket
import ujson
import ahtx0

from umqtt.simple import MQTTClient 
from umqtt.simple import MQTTException

mqtterrortable=["Connection Accepted", "Connection Refused, Unacceptable Protocol Version","Connection Refused, Identifier Rejected","Connection Refused, Server Unavailable", "Connection Refused, Bad Username or Password", "Connection Refused, Not Authorized"]

#Configure pinout
LED = machine.Pin(15, machine.Pin.OUT) 
LED2 = machine.Pin(16, machine.Pin.OUT) 
BUTTON1 = Pin(20, Pin.IN) 
BUTTON2 = Pin(21, Pin.IN) 
BUTTON3 = Pin(22, Pin.IN) 

#Set initial values for LEDs
LED.value(0)
LED2.value(0)

#Initialize temperature sensor via I2C interface
i2c1 = I2C(id=1, scl=Pin(3), sda=Pin(2), freq=400_000) 
tmp_sensor = ahtx0.AHT20(i2c1) 

#Create MQTT Client with keepalive of 60 seconds
SERVER_IP = "86.49.182.194"
CLIENT_ID = "IoT_06" 
ACCESS_TOKEN = "IoT_00" 
keepalive_seconds = 60 
REMOTE_PORT = 36102
client = MQTTClient(CLIENT_ID,SERVER_IP, user=ACCESS_TOKEN, password="",keepalive=keepalive_seconds, port=REMOTE_PORT)

#Configure Interrupt handlers when buttons are pressed.
def pinWaitForPinReturn(pin):
    pin.irq(trigger=Pin.IRQ_FALLING, handler=pinPressedCallback)
    time.sleep(0.1)
    json_string={"20":BUTTON1.value()!=True,"21":BUTTON2.value()!=True,"22":BUTTON3.value()!=True}
    print(f"Sending json message: {json_string}")
    json = ujson.dumps(json_string)
    client.publish(b"v1/devices/me/telemetry",json)

def pinPressedCallback(pin):
    global client
    time.sleep(0.1)
    json_string={"20":BUTTON1.value()!=True,"21":BUTTON2.value()!=True,"22":BUTTON3.value()!=True}
    print(f"Sending json message: {json_string}")
    json = ujson.dumps(json_string)
    client.publish(b"v1/devices/me/telemetry",json)
    print(json)
    print("Button Pressed. " + str(pin))
    pin.irq(trigger=Pin.IRQ_RISING, handler=pinWaitForPinReturn)
    
#Assign interrupt handlers to a specific button event.
BUTTON1.irq(trigger=Pin.IRQ_FALLING, handler=pinPressedCallback)
BUTTON2.irq(trigger=Pin.IRQ_FALLING, handler=pinPressedCallback)
BUTTON3.irq(trigger=Pin.IRQ_FALLING, handler=pinPressedCallback)
time.sleep(5)

#Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True) # enable Wi-Fi interface
wlan.connect("LPWAN-IoT-06", "LPWAN-IoT-06-WiFi")

# while Wi-Fi is not connected
while not wlan.isconnected():
    
    print("WIFI STATUS CONNECTED: " + str(wlan.isconnected())) # print current status aka False=Not connect, True=Connected
        
    time.sleep_ms(1000) 
print(wlan.ifconfig())

#MQTT
def on_message_callback(topic, msg):
    print((topic, msg))
    js = ujson.loads(msg)
    print(js)
    if 'v1/devices/me/rpc/request/' in topic:
        print("Yep, it's and RPC request.")
        if js['params']:
            LED2.value(1)
        else:
            LED2.value(0)
    elif 'v1/devices/me/attributes' in topic:
        print(js['LED_GP15'])
        if js['LED_GP15']:
            LED.value(1)
        else:
            LED.value(0)
    else:
        print("Unknown message")
    
#Assign the callback to the MQTT client
client.set_callback(on_message_callback)

#Connect the client to the server and subscribe to desired topics.
try:
    client.connect()
    client.subscribe(b"v1/devices/me/attributes") 
    client.subscribe(b"v1/devices/me/rpc/request/+")
except MQTTException as mqtte:
    print("MQTTException : " + str(mqtte)  + " - " + mqtterrortable[int(str(mqtte))])
except:
    print("Other Error")

#Counters that will keep track of time.
mqtt_ctr = 0
seconds_counter = 0

#Infinite loop
print("Entering infinite loop")
while True:
    try:
       
        client.check_msg()
        mqtt_ctr = mqtt_ctr+1
        seconds_counter=seconds_counter+1
        
        if mqtt_ctr >= (keepalive_seconds-2)/0.1:
            mqtt_ctr = 0
            client.ping()
                   
        if seconds_counter >= 10/0.1:
            seconds_counter=0
            json_string={"teplota":tmp_sensor.temperature, "vlhkost":tmp_sensor.relative_humidity}
            print(f"Sending json message: {json_string}")
            json = ujson.dumps(json_string)
            client.publish(b"v1/devices/me/telemetry",json)
        if not BUTTON1.value(): 
            json_string={"teplota":tmp_sensor.temperature, "vlhkost":tmp_sensor.relative_humidity}
            print(f"Sending json message: {json_string}")
            json = ujson.dumps(json_string)
            client.publish(b"v1/devices/me/telemetry",json)
    except Exception as exception:
        print("Error: " + str(exception))
        
    time.sleep(0.1)
    
client.disconnect()