# !/usr/bin/python3
import random
import string

import serial
import time

class NBIoT:
    BASIC_TIMEOUT = 0.1
    LONG_TIMEOUT = 10

    FLAG_000 = "0x000"
    FLAG_200 = "0x200"
    FLAG_400 = "0x400"

    REPORT_CONNECTION_STATUS = "+CSCON"
    REPORT_PSM = "+NPSMR"
    REPORT_MESSAGE_ACK = "+NSMI"
    REPORT_OTA = "+UFOTAS"
    REPORT_CEREG = "+CEREG"

    BAND_20 = 20
    BAND_8 = 8

    POWER_CLASS_3 = 3
    POWER_CLASS_5 = 5

    CEREG_DEFAULT = 0
    CEREG_REGISTRATION = 1
    CEREG_REGISTRATION_LOCATION = 2
    CEREG_REGISTRATION_LOCATION_EMM = 3
    CEREG_REGISTRATION_LOCATION_PSM = 4
    CEREG_FULL = 5

    NUESTATS_RADIO = "RADIO"
    NUESTATS_CELL = "CELL"
    NUESTATS_BLER = "BLER"
    NUESTATS_THP = "THP"
    NUESTATS_APPSMEM = "APPSMEM"
    NUESTATS_ALL = "ALL"

    def __init__(self, comport, speed):
        self.comport = serial.Serial(comport, speed, timeout=.5)

    def send_raw_command(self, command):
        print(command)
        command += "\r\n"
        self.comport.write(command.encode())
        in_time = time.time()

    def read_data(self, timeout):
        started = time.time()
        buffer = ""
        while not self.comport.inWaiting():
            if time.time() - started > timeout:
                print("No response from module, Timeout ERROR")
                return

        last_rx = time.time()
        in_time = str(round(last_rx * 1000))
        while time.time() - last_rx < 0.04:
            if self.comport.inWaiting():
                last_rx = time.time()
                rx_char = str(self.comport.read(), 'utf-8', errors='ignore')
                if rx_char is not None:
                    buffer += rx_char
            time.sleep(0.001)
        buffer = "".join([s for s in buffer.strip().splitlines(True) if s.strip("\r\n")])
        print(buffer)
        return buffer

    def reboot_module(self):
        self.send_raw_command("AT+NRB")
        retry_count = 0
        while True:
            data = self.read_data(self.LONG_TIMEOUT)
            if data is None: continue
            retry_count += 1
            if retry_count > 5 or "OK" in data:
                break

    def switch_radio(self, on):
        self.send_raw_command("AT+CFUN=" + str(on))
        self.read_data(self.LONG_TIMEOUT)

    def set_status_report(self, report_type, state):
        self.send_raw_command("AT" + report_type + "=" + str(state))
        self.read_data(self.BASIC_TIMEOUT)

    def set_operator(self, operator_number):
        self.send_raw_command("AT+COPS=1,2,\"" + operator_number + "\"")
        self.read_data(self.BASIC_TIMEOUT)

    def is_operator_set(self, operator_number):
        exp_response = "+COPS: 1,2,\"" + operator_number + "\""
        self.send_raw_command("AT+COPS?")
        if exp_response in self.read_data(self.BASIC_TIMEOUT):
            return True
        else:
            return False

    def is_attached(self):
        self.send_raw_command("AT+CGATT?")
        if "+CGATT: 1" in self.read_data(self.BASIC_TIMEOUT + 0.5):
            return True
        else:
            return False

    def set_apn_name(self, apn_name):
        self.send_raw_command("AT+CGDCONT=1,\"IP\",\"" + apn_name + "\"")
        self.read_data(self.BASIC_TIMEOUT)

    def open_socket(self, port):
        self.send_raw_command("AT+NSOCR=\"DGRAM\",17," + str(port) + ",1")
        response = self.read_data(self.BASIC_TIMEOUT)
        return int(response[0])

    def close_socket(self, socket):
        self.send_raw_command("AT+NSOCL=" + str(socket))
        self.read_data(self.BASIC_TIMEOUT)

    @staticmethod
    def generate_random_message(length):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    @staticmethod
    def generate_char_message(length, char):
        return ''.join([ch * int(length) for ch in char])

    def send_message(self, message, remote_ip, remote_port, flag, socket):
        if len(message) > 512:
            print("The maximum length is 512 bytes!")
            return
        encoded_message = ("".join("{:02x}".format(ord(c)) for c in message))
        self.send_raw_command("AT+NSOSTF=" + str(socket) + ",\"" + remote_ip +
                              "\"," + str(remote_port) + "," + flag + "," +
                              str(len(message)) + ",\"" + encoded_message + "\"")
        self.read_data(3 * self.BASIC_TIMEOUT)

    def wait_for_message(self, timeout):
        start = time.time()
        while not self.comport.inWaiting():
            if time.time() - start > timeout:
                print("No message has been received!")
                return [-1, -1]
        data = self.read_data(self.BASIC_TIMEOUT)
        end = time.time()
        print("Time from fun: ", end-start)
        return (data[9:len(data)]).split(",")

    def read_message(self, socket, length):
        self.send_raw_command("AT+NSORF=" + str(socket) + "," + str(length))	#přidán str() (převod)
        data = self.read_data(self.BASIC_TIMEOUT)
        data_list = data[2: len(data) - 2].split(",")
        resp_dict = {"ip": -1, "port": -1, "length": -1, "raw_message": -1, "remain_length": -1}
        for i, (k, v) in enumerate(resp_dict.items()):
            if data_list[i][0] == '\"':
                resp_dict[k] = data_list[i].replace('"', '')
            else:
                resp_dict[k] = int(data_list[i])
        resp_dict["message"] = bytes.fromhex(resp_dict["raw_message"]).decode("ascii")
        return resp_dict

    def wait_for_report(self, report_type, timeout):
        start = time.time()
        while not self.comport.inWaiting():
            if time.time() - start > timeout:
                print("No message has been received!")
                return -1
        data = self.read_data(self.BASIC_TIMEOUT)
        if report_type in data:
            return data.split(" ")[1][0]
        else:
            print("Wrong report received")

    def set_band(self, band):
        self.send_raw_command("AT+NBAND=" + str(band))
        self.read_data(self.BASIC_TIMEOUT)

    def set_power_class(self, power_class, band):
        self.send_raw_command("AT+NPOWERCLASS=" + str(band) + "," + str(power_class))
        self.read_data(self.BASIC_TIMEOUT)

    def get_power_class(self):
        self.send_raw_command("AT+NPOWERCLASS?")
        self.read_data(self.BASIC_TIMEOUT)

    def set_cereg(self, cereg_level):
        self.send_raw_command("AT+CEREG=" + str(cereg_level))
        self.read_data(self.BASIC_TIMEOUT)

    def get_cereg(self):
        self.send_raw_command("AT+CEREG?")
        self.read_data(self.BASIC_TIMEOUT)

    def disable_psm(self):
        self.send_raw_command("AT+CPSMS=0")
        self.read_data(self.BASIC_TIMEOUT)

    def enable_psm(self, active_timer, periodic_timer):
        self.send_raw_command("AT+CPSMS=1,,,\"" + str(periodic_timer) + "\",\"" + str(active_timer) + "\"")
        self.read_data(self.BASIC_TIMEOUT)

    def get_signal_quality(self):
        self.send_raw_command("AT+CSQ")
        self.read_data(self.BASIC_TIMEOUT)

    def get_manufacturer(self):
        self.send_raw_command("AT+CGMI")
        self.read_data(self.BASIC_TIMEOUT)

    def get_model(self):
        self.send_raw_command("AT+CGMM")
        self.read_data(self.BASIC_TIMEOUT)

    def get_firmware_version(self):
        self.send_raw_command("AT+CGMR")
        self.read_data(self.BASIC_TIMEOUT)

    def get_imsi(self):
        self.send_raw_command("AT+CIMI")
        self.read_data(self.BASIC_TIMEOUT)

    def get_imei(self):
        self.send_raw_command("AT+CGSN=1")
        self.read_data(self.BASIC_TIMEOUT)

    def get_iccid(self):
        self.send_raw_command("AT+CCID?")
        self.read_data(self.BASIC_TIMEOUT)

    def empty_at(self):
        self.send_raw_command("AT")
        self.read_data(self.BASIC_TIMEOUT)

    def ping_to_remote(self, remote_ip, size, timeout):
        start = time.time()
        if size < 8 or size > 1460:
            print("Packed size is not in allowed range (8-1460)!")
            return

        if timeout < 10 or timeout > 60000:
            print("The ping timeout is not in allowed range (10-60000ms)")

        self.send_raw_command("AT+NPING=\"" + remote_ip + "\"," + str(size) + "," + str(timeout))
        self.read_data(self.BASIC_TIMEOUT)
        start = time.time()
        while not self.comport.inWaiting():
            if time.time() - start > timeout + 500:
                print("No message has been received!")
                return

        data = self.read_data(self.BASIC_TIMEOUT)

        if "+NPINGERR:" in data:
            print("Ping request failure!")
            return

        if "+NPING:" in data:
            split_data = data.split(",")
            end = time.time()
            print("Time from fun ping: ", end-start, "[s]")
            return [int(split_data[1]), int(split_data[2].strip("\r\n"))]
        
        

    def get_stats(self, stat_type):
        self.send_raw_command("AT+NUESTATS=\"" + stat_type + "\"")
        data = ""
        in_time = str(round(time.time() * 1000))
        while True:
            line = str(self.comport.readline(), 'utf-8', errors='replace')
            if "\r\n" != line:
                data += line
                print(line, end="")
            if ("OK\r\n" in line) or ("ERROR\r\n" in line):
                break
