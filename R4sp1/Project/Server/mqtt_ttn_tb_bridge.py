#!/usr/bin/python3
import paho.mqtt.client as mqtt
import json
import sys
import string
import getopt
import base64
from termcolor import colored, cprint
import datetime
import math
import time

APPID = 'but-biot@ttn'
PSW = 'NNSXS.6Y2R3MM35VECHE5QW5MWBI4GO7FNCAQV2JVGTTI.XIBWN4ADZ6JZQFCIKV6HKDN5AA2YTMDAPIPG6VVJMU77DYWPEHZA'

tb_client = mqtt.Client()

# Thingsboard functions

# when connected to server
def on_connect_tb(client, userdata, flags, rc):
    client.subscribe('v1/devices/me/attributes')
    print("===========================================================================")
    print("\t\t\tConnected to Thingboard")
    print("\t\t\tServer Host:{} Port: {}".format(client._host, client._port))
    print("\t\t\tAccess Credential:{}".format(client._username))
    print("===========================================================================")

# when receiving message
def on_message_tb(client, userdata, msg):
    #j_msg = json.loads(msg.payload.decode('utf-8'))
    print("Received message on topic: {} with message: {}".format(msg.topic, msg.payload))

# The Things Networks functions
def on_connect(client, userdata, flags, rc):
    client.subscribe('v3/{}/devices/eui-{}/up'.format(APPID, userdata.lower()))
    print("===========================================================================")
    print("\t\t\tConnected The Things Network")
    print("\t\t\tServer Host:{} Port: {}".format(client._host, client._port))
    print("\t\t\tAccess Credential:{}".format(client._username))
    print("===========================================================================")

# when receiving message
def on_message(client, userdata, msg):
    j_msg = json.loads(msg.payload.decode('utf-8'))
    print(msg.topic)
    try:
        if userdata == j_msg['end_device_ids']['dev_eui']:
            message = base64.b64decode(j_msg['uplink_message']['frm_payload']).hex()
            message_dec = bytearray.fromhex(message).decode()
            cr = str(j_msg['uplink_message']['settings']['data_rate']['lora']['coding_rate'])

            cr_int = int(cr[cr.find('/') + 1:])
            # dr = str(j_msg['settings']['data_rate']['lora']['bandwidth'])
            sf = int(j_msg['uplink_message']['settings']['data_rate']['lora']['spreading_factor'])
            bw = int(j_msg['uplink_message']['settings']['data_rate']['lora']['bandwidth'] / 1000)
            # t_symbol = 2**sf / bw * 1.0
            # t_preamble = 12.25 * t_symbol
            # t_payload = t_symbol * (8 + max(math.ceil((8 * len(message_dec) - 4 * sf + 44)/(4 * sf)), 0) * cr_int)
            # air_time = t_preamble + t_payload
            print("===========================================================================")
            now = datetime.datetime.now()
            cprint("NEW MESSAGE >> " + str(now.strftime("%H:%M:%S %d-%m-%Y")), "red")
            print("===========================================================================")
            print(colored("Raw message: ", "yellow"), end="")
            print(message)
            print(colored("Decoded message: ", "yellow"), end="")
            print(message_dec)
            print(colored("Port: ", "yellow"), end="")
            print(j_msg['uplink_message']['f_port'])
            print(colored("Counter: ", "yellow"), end="")
            print(j_msg['uplink_message']['f_cnt'])
            print(colored("SF: ", "yellow"), end="")
            print(j_msg['uplink_message']['settings']['data_rate']['lora']['spreading_factor'])
            print(colored("Airtime: ", "yellow"), end="")
            cons_time = float(j_msg['uplink_message']['consumed_airtime'][:-1]) * 1000
            print(f'{cons_time:.3f} ms')
            # print(colored("Airtime: ", "yellow"), end="")
            # print(f'{air_time:.3f} ms')
            print(colored("Frequency: ", "yellow"), end="")
            print(j_msg['uplink_message']['settings']['frequency'])
            # print(colored("Data rate: ", "yellow"), end="")
            # print(j_msg["metadata"]["data_rate"])
            print(colored("Coding rate: ", "yellow"), end="")
            print(cr)

            ################################################################################################################################
            # if Thingsboard connector is in state "Connected", parse and send received data from LoRaWAN The Things Network to Thingsboard
            ################################################################################################################################
            if tb_client.is_connected():
                tb_msg = {}
                parts = str(message_dec).split('b')
                tb_msg['longitude'] = parts[0]
                tb_msg['latitude'] = parts[1]

                # publish data to topic v1/devices/me/attributes for attributes or v1/devices/me/telemetry for telemetry (data with timestamp)
                # payload must be as string
                # payload example {"user_data": ""}
                tb_client.publish(topic='v1/devices/me/telemetry', payload=str(tb_msg))

            if j_msg['uplink_message']['rx_metadata'] is not None:
                for gw in j_msg['uplink_message']['rx_metadata']:
                    print("===========================================================================")
                    print(colored("Gateway: ", "green"), end="")
                    print(gw['gateway_ids']['gateway_id'])
                    print(colored("Gateway EUI: ", "green"), end="")
                    print(gw['gateway_ids']['eui'])
                    if 'channel_index' in gw:
                        print(colored("Channel: ", "green"), end="")
                        print(str(gw['channel_index']))
                    print(colored("RSSI: ", "green"), end="")
                    print(str(gw['rssi']))
                    print(colored("SNR: ", "green"), end="")
                    print(str(gw['snr']))
                    print("===========================================================================")
    except KeyError:
        print("===========================================================================")
        print(colored("Wrong packet format", "red"), end="\n")
        print("===========================================================================")



def is_hex_str(s):
    return set(s).issubset(string.hexdigits)


def main(argv):
    dev_eui = ""
    tb_dev_credentials = ""
    try:
        opts, args = getopt.getopt(argv, "d:c:", ["devui=","tbcred="])
    except getopt.GetoptError:
        print("Error")
        print("mqtt_client.py -d <Device EUI> -c <TB Device Access Credential>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("mqtt_client.py -d <Device EUI> -c <TB Device Access Credential>")
            sys.exit()
        elif opt in ("-d", "--devui"):
            dev_eui = arg
        elif opt in ("-c", "--tbcred"):
            tb_dev_credentials = str(arg)

    if not is_hex_str(dev_eui):
        cprint("Invalid device EUI", "red")
        sys.exit(-1)

    if len(dev_eui) == 0:
        cprint("Missing device EUI", "red")
        sys.exit(-1)

    if len(tb_dev_credentials) == 0:
        cprint("Missing Thingsboard device access credentials", "red")
        sys.exit(-1)

    ttn_client = mqtt.Client()
    ttn_client.user_data_set(dev_eui)
    ttn_client.on_connect = on_connect
    ttn_client.on_message = on_message
    ttn_client.username_pw_set(APPID, PSW)
    ttn_client.connect("eu1.cloud.thethings.network", 1883, 60)  # MQTT port over TLS

    #"TTN_TB_Device_01"

    tb_client.on_connect = on_connect_tb
    tb_client.on_message = on_message_tb
    tb_client.username_pw_set(tb_dev_credentials)
    tb_client.connect(host="86.49.182.194", port=36102)  # MQTT port over TLS


    try:
        #ttn_client.loop_forever()
        #tb_client.loop_forever()
        while True:
            ttn_client.loop_start()
            tb_client.loop_start()
            time.sleep(0.001)
    except KeyboardInterrupt:
        ttn_client.loop_stop()
        tb_client.loop_stop()
        ttn_client.disconnect()
        print('Disconnected')
        print("===========================================================================")


if __name__ == "__main__":
    main(sys.argv[1:])
