#!/usr/bin/python3
import sys
import getopt
import socket
#import netifaces as ni
#from termcolor import colored, cprint
import datetime
import time

IP_ADDRESS = "192.168.137.1"

def get_ip_address(interface):
    '''ni.ifaddresses(interface)
    ip = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']'''
    return IP_ADDRESS


def udp(address, port, echo):
    try:
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind((address, port))
        print("=======================================================================")
        print("\t\t\tUDP server is running")
        print("=======================================================================")
        while True:
            data, addr = udp_socket.recvfrom(1024)
            print("New message >> " + str(datetime.datetime.now().strftime("%H:%M:%S %d-%m-%Y")))
            print("=======================================================================")
            print("Data: ", end="")
            print(data.decode())
            if echo is True:
                time.sleep(1)
                udp_socket.sendto(data, addr)
            print("=======================================================================")
    except KeyboardInterrupt:
        print("\t\tUDP server stopped")
        print("=======================================================================")


def tcp(address, port, echo):
    try:
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.bind((address, port))
        tcp_socket.listen(1)
        print("=======================================================================")
        print("\t\t\tTCP server is running")
        print("=======================================================================")
        conn, addr = tcp_socket.accept()
        print("Client connected: " + str(addr))
        print("=======================================================================")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            else:
                print("New message >> " + str(datetime.datetime.now().strftime("%H:%M:%S %d-%m-%Y")))
                print("=======================================================================")
                print("Data: ", end="")
                print(data.decode())
                if echo is True:
                    time.sleep(1)
                    conn.send(data)
                print("=======================================================================")
        print("Connection closed")
        print("=======================================================================")
    except KeyboardInterrupt:
        print("\t\tTCP server stopped")
        print("=======================================================================")


def main(argv):
    port = 0
    mode = ""
    interface = ""
    echo = False

    try:
        opts, args = getopt.getopt(argv, "h:m:p:e:", ["mode=", "port=", "echo="])
    except getopt.GetoptError:
        print("Error")
        print("esp_server.py -m <TCP/UDP> -p <Port> -e <on/off>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("esp_server.py -m <TCP/UDP> -p <Port> -e <on/off>")
            sys.exit()
        elif opt in ("-m", "--mode"):
            mode = str(arg)
        elif opt in ("-p", "--port"):
            port = int(arg)
        elif opt in ("-e", "--echo"):
            if str(arg).lower() == "on":
                echo = True

    if port <= 0 or port > 65535:
        print("Invalid port")
        sys.exit(-1) 

    address = get_ip_address(interface)

    if mode == "TCP":
        tcp(address, port, echo)
    elif mode == "UDP":
        udp(address, port, echo)
    else:
        print("Invalid mode!")
        sys.exit(-1)


if __name__ == "__main__":
    main(sys.argv[1:])
