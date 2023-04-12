# !/usr/bin/python3
import random
import string

import serial
import time

class NBIoT:
    # timeout list
    BASIC_TIMEOUT = 0.100 # in s
    LONG_TIMEOUT = 10 # in s

    # flag list
    FLAG_000 = "0x000" # 0x000: no flags are set
    FLAG_200 = "0x200" # 0x200: release indicator. Indicate release after next message
    FLAG_400 = "0x400" # 0x400: release indicator. Indicate release after next message has been replied to

    # report list
    REPORT_CONNECTION_STATUS = "+CSCON" # Signalling connection status
    REPORT_PSM = "+NPSMR" # Power saving mode status
    REPORT_MESSAGE_ACK = "+NSMI" #Send message indication
    REPORT_OTA = "+UFOTAS" # Firmware update status
    REPORT_CEREG = "+CEREG" # Network registration status

    # band list
    BAND_20 = 20
    BAND_8 = 8

    # power class list
    POWER_CLASS_3 = 3
    POWER_CLASS_5 = 5

    # network registration status mode list
    CEREG_DEFAULT = 0
    CEREG_REGISTRATION = 1
    CEREG_REGISTRATION_LOCATION = 2
    CEREG_REGISTRATION_LOCATION_EMM = 3
    CEREG_REGISTRATION_LOCATION_PSM = 4
    CEREG_FULL = 5

    # nuestats report list
    NUESTATS_RADIO = "RADIO"
    NUESTATS_CELL = "CELL"
    NUESTATS_BLER = "BLER"
    NUESTATS_THP = "THP"
    NUESTATS_APPSMEM = "APPSMEM"
    NUESTATS_ALL = "ALL"

    def __init__(self, comport, speed):
        """Internal init function

        :param comport: serial port, example: "COM15"
        :param speed: serial port baudrate speed, example: 9600
        :return: None
        """
        self.comport = serial.Serial(comport, speed, timeout=.5)

    def send_raw_command(self, command):
        """Function to send RAW AT commands according to AT specifications for comm. module

        :param command: AT command according to AT specifiction for comm. module, example: "AT+CGMI"
        :return: Received response from comm. module
        """
        
        print(f"Sending raw command: {command}")
        command += "\r\n"
        
        
        
        
        self.comport.write(command.encode())
        in_time = time.time()

    def read_data(self, timeout):
        """Function to read data from module's receive buffer

        :param timeout: timeout interval in ms
        :return: received data or None for no response in timeout interval
        """
        
        started = time.time()
        buffer = ""
        while not self.comport.inWaiting():
            if time.time() - started > timeout:
                print("No response from module, Timeout ERROR")
                return None

        last_rx = time.time()
        in_time = str(round(last_rx * 1000))
        while time.time() - last_rx < 0.40:
            if self.comport.inWaiting():
                last_rx = time.time()
                rx_char = str(self.comport.read(), 'utf-8', errors='ignore')
                if rx_char is not None:
                    buffer += rx_char
            time.sleep(0.001)
            
        buffer = "".join([s for s in buffer.strip().splitlines(True) if s.strip("\r\n")])
        print(f"Received data: {buffer}")
        
        return buffer

    def reboot_module(self):
        """Function to reboot/soft-reset comm. module

        :return: True after reboot
        """
        print("Reboot RF module")
        self.send_raw_command("AT+NRB")
        retry_count = 0
        while True:
            data = self.read_data(self.LONG_TIMEOUT)
            if data is None: continue
            retry_count += 1
            print(f"Retry count: {retry_count}")
            if retry_count > 5 or "OK" in data:
                break
            
        return True

    def switch_radio(self, on):
        """Function to enable radio circuitry on comm. module
            example: return from airplane mode or low-power mode

        :param on: state of RF circuit, either 1/on/True or 0/off/False
        """
        
        if on == 1 or on == True or on == "on":
            on = 1
            print("Module RF circuits: ON")
        elif on == 0 or on == False or on == "off":
            on = 0
            print("Module RF circuits: OFF")
        else:
            on = 0
            print("Module RF circuits: OFF-DEFAULT")
            
        self.send_raw_command("AT+CFUN=" + str(on))
        self.read_data(self.LONG_TIMEOUT)
        
    def get_radio_circuit_state(self):
        """Get current state of module RF circuits

        :return: 1 for ON state, 0 for OFF state
        """
        
        self.send_raw_command("AT+CFUN?")
        recv_data = self.read_data(self.BASIC_TIMEOUT + 0.500)
        
        if "+CFUN: 1" in recv_data:
            print("Module RF circuits: ON")
            return 1
        elif "+CFUN: 0" in recv_data:
            print("Module RF circuits: OFF")
            return 0
        else:
            print("Module RF circuits: Unknown")
            return 0

    def get_status_report(self, report_type):
        """Receive latest report for specified report type

        :param report_type: selected report type to be enabled/disabled
        :return: received data in dict format
        """
        
        self.send_raw_command("AT+NUESTATS=\"" + str(report_type) + "\"")
        
        return self.wait_for_report(report_type, 30)
    
    def set_status_report(self, report_type, state):
        """Enable/disable specified report to be reported from comm. module back to master/pc

        :param state: 1/on/True (enable report) or 0/off/False (disable report)
        """
        
        if state == 1 or state == True or state == "on":
            state = 1
            print(f"Report {report_type}: ENABLED")
        elif state == 0 or state == False or state == "off":
            state = 0
            print(f"Report {report_type}: DISABLED")
        else:
            state = 0
            print(f"Report {report_type}: DISABLED")
        
        self.send_raw_command("AT+" + str(report_type) + "=" + str(state))
        return self.read_data(self.BASIC_TIMEOUT)

    def wait_for_report(self, report_type, timeout):
        """Function to wait and catch status reply for specified report

        :param report_type: serial port example: "COM15"
        :param timeout: timeout interval in ms
        :return: received data in list or dict format depending on report
        """
        
        start = time.time()
        while not self.comport.inWaiting():
            if time.time() - start > timeout:
                print("No message has been received!")
                return False
            
        data = self.read_data(self.BASIC_TIMEOUT)
        
        if report_type in data or report_type == self.NUESTATS_ALL:
            print("Correct report received")
        else:
            print("Wrong report received")

        
        if "OK" in data:
            data = data.replace("\r\nOK","")
        
        if report_type == self.NUESTATS_CELL or report_type == self.NUESTATS_ALL:
            return data
        else:
            dataBasic = data.replace("\r\n",",")
            cleanLines = dataBasic.replace("NUESTATS: \"" + str(report_type) + "\",", "")
            dataLines = cleanLines.split(",")
            
            parsed_data = {}
            count = 0
            while count < len(dataLines):
                parsed_data[dataLines[count]] = dataLines[count+1]
                count +=2
            
            return parsed_data
            
    def set_operator(self, operator_number):
        """Function to set operator by unique identification number

        :param operator_number: specific operator number, example: 23003 (Vodafone)
        """
        
        self.send_raw_command("AT+COPS=1,2,\"" + str(operator_number) + "\"")
        self.read_data(self.BASIC_TIMEOUT)

    def is_operator_set(self, operator_number):
        """Function to validate if correct operator number is set

        :param operator_number: specific operator number, example: 23003 (Vodafone)
        :return: True (operator number matches with expected value), False otherwise
        """
        
        exp_response = "+COPS: 1,2,\"" + str(operator_number) + "\""
        self.send_raw_command("AT+COPS?")
        
        if exp_response in self.read_data(self.BASIC_TIMEOUT):
            return True
        else:
            return False

    def is_attached(self):
        """Function to check if comm. module is attached/registered to mobile network

        :return: True (if attached/registered), False otherwise
        """
        
        self.send_raw_command("AT+CGATT?")
        if "+CGATT: 1" in self.read_data(self.BASIC_TIMEOUT + 0.5):
            return True
        else:
            return False

    def set_apn_name(self, apn_name):
        """Function to set APN

        :param apn_name: APN name, example apn.vodafone.cz
        :param speed: serial port baudrate speed example: 9600
        :return: None
        """
        
        self.send_raw_command("AT+CGDCONT=1,\"IP\",\"" + str(apn_name) + "\"")
        self.read_data(self.BASIC_TIMEOUT)

    def open_socket(self, port):
        """Function to set-up and open socket on comm. module

        :param port: transport layer (L4) port to be opened, example: 80 (http)
        :return: comm. module's internal socket number, which is used as reference for other AT commands
        """
        
        self.send_raw_command("AT+NSOCR=\"DGRAM\",17," + str(port) + ",1")
        response = self.read_data(self.BASIC_TIMEOUT)
        return int(response[0])

    def close_socket(self, socket):
        """Function to close opened socket on comm. module

        :param socket: comm. module's internal socket number, example: 1
        """
        
        self.send_raw_command("AT+NSOCL=" + str(socket))
        self.read_data(self.BASIC_TIMEOUT)

    @staticmethod
    def generate_random_message(length):
        """Function to generate random message with defined length

        :param length: wanted length of message in characters, example: 50 (50 char message)
        :return: generated random message
        """
        
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    @staticmethod
    def generate_char_message(length, char):
        """Function to generate random message with defined length and specified characters

        :param length: wanted length of message in characters, example: 50 (50 char message)
        :param char: list of characters, which will be placed in message, example: "ABCD"
        :return: generated random message
        """
        
        return ''.join([ch * int(length) for ch in char])

    def send_message(self, message, remote_ip, remote_port, flag, socket):
        """Function to send message

        :param message: message to be send
        :param remote_ip: IP address of receiver
        :param remote_port: transport layer port of receiver
        :param flag: type of message transmission 
        :param socket: comm. module's internal socket number, example: 1 
        """
        
        if len(message) > 512:
            print("The maximum length is 512 bytes!")
            return
        encoded_message = ("".join("{:02x}".format(ord(c)) for c in message))
        self.send_raw_command("AT+NSOSTF=" + str(socket) + ",\"" + str(remote_ip) +
                              "\"," + str(remote_port) + "," + str(flag) + "," +
                              str(len(message)) + ",\"" + encoded_message + "\"")
        self.read_data(3 * self.BASIC_TIMEOUT)

    def wait_for_message(self, timeout):
        """Function to wait for report from comm. module about message receival

        :param timeout: timeout interval in ms
        :return: list [socket, size of received data (in characters)] 
        """
        
        start = time.time()
        while not self.comport.inWaiting():
            if time.time() - start > timeout:
                print("No message has been received!")
                return [-1, -1]
        data = self.read_data(self.BASIC_TIMEOUT)
        split_data = (data[9:len(data)]).split(",")
        
        return [split_data[0], split_data[1]]

    def read_message(self, socket, length):
        """Function to request received message data

        :param socket: comm. module's internal socket number, example: 1
        :param length: wanted length of message in characters, example: 50 (50 char message)
        :return: received message with additional information as dict
        """
        
        self.send_raw_command("AT+NSORF=" + str(socket) + "," + str(length))
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

    def set_band(self, band):
        """Function to set transmission band

        :param band: selected band according to specs.
        """
        
        self.send_raw_command("AT+NBAND=" + str(band))
        self.read_data(self.BASIC_TIMEOUT)

    def set_power_class(self, power_class, band):
        """Function to set transmission power for specified band

        :param power_class: transmission power
        :param band: selected band according to specs.
        :return: None
        """
        
        self.send_raw_command("AT+NPOWERCLASS=" + str(band) + "," + str(power_class))
        self.read_data(self.BASIC_TIMEOUT)

    def get_power_class(self):
        """Function to read currently set power class from comm. module

        :return: None
        """
        
        self.send_raw_command("AT+NPOWERCLASS?")
        self.read_data(self.BASIC_TIMEOUT)

    def set_cereg(self, cereg_level):
        """Function to set CEREG mode

        :param cereg_level: cereg mode, see AT spec.
        """
        
        self.send_raw_command("AT+CEREG=" + str(cereg_level))
        self.read_data(self.BASIC_TIMEOUT)

    def get_cereg(self):
        """Function to get currently set CEREG mode

        :return: None
        """
        
        self.send_raw_command("AT+CEREG?")
        self.read_data(self.BASIC_TIMEOUT)

    def disable_psm(self):
        """Function to disable PSM (Power Saving Mode) for comm. module

        """
        
        self.send_raw_command("AT+CPSMS=0")
        self.read_data(self.BASIC_TIMEOUT)

    def enable_psm(self, active_timer, periodic_timer):
        """Function to enable PSM (Power Saving Mode) based on provided T3324 (Active Time) and T3412 (Extended TAU Timer)

        :param active_timer: T3324 timer
        :param periodic_timer: T3412 timer
        """
        
        self.send_raw_command("AT+CPSMS=1,,,\"" + periodic_timer + "\",\"" + active_timer + "\"")
        self.read_data(self.BASIC_TIMEOUT)

    def get_signal_quality(self):
        """Function to request signal quality

        :return: Raw +CSQ reply
        """
        
        self.send_raw_command("AT+CSQ")
        recv = self.read_data(self.BASIC_TIMEOUT)
        return str(recv)

    def get_manufacturer(self):
        """Function to read manufacturer info from comm. module

        :return: string with manufacturer name
        """
        
        self.send_raw_command("AT+CGMI")
        recv = self.read_data(self.BASIC_TIMEOUT)
        return str(recv)

    def get_model(self):
        """Function to read comm. module model

        :return: string with model number
        """
        
        self.send_raw_command("AT+CGMM")
        recv = self.read_data(self.BASIC_TIMEOUT)
        return str(recv)

    def get_firmware_version(self):
        """Function to read comm. module model

        :return: string with FW version
        """
        
        self.send_raw_command("AT+CGMR")
        recv = self.read_data(self.BASIC_TIMEOUT)
        return str(recv)

    def get_imsi(self):
        """Function to read comm. module model

        :return: IMSI
        """
        
        self.send_raw_command("AT+CIMI")
        recv = self.read_data(self.BASIC_TIMEOUT)
        return str(recv)

    def get_imei(self):
        """Function to read comm. module model

        :return: IMEI
        """
        
        self.send_raw_command("AT+CGSN=1")
        recv = self.read_data(self.BASIC_TIMEOUT)
        return str(recv)

    def get_iccid(self):
        """Function to read comm. module model

        :return: ICCID
        """
        
        self.send_raw_command("AT+CCID?")
        recv = self.read_data(self.BASIC_TIMEOUT)
        
        split_data = recv.split(":")
        return str(split_data[1])

    def empty_at(self):
        """Test function to check if communication between master and comm. module works as expected

        """
        
        self.send_raw_command("AT")
        self.read_data(self.BASIC_TIMEOUT)

    def ping_to_remote(self, remote_ip, size, timeout):
        """Function to ping to specified remote address

        :param remote_ip: IP address of remote host
        :param size: size of packets send to remote host
        :param timeout: timeout interval in ms
        :return: list [TTL, RTT]
        """
        
        if size < 8 or size > 1460:
            print("Packed size is not in allowed range (8-1460)!")
            return

        if timeout < 10 or timeout > 60000:
            print("The ping timeout is not in allowed range (10-60000ms)")

        self.send_raw_command("AT+NPING=\"" + str(remote_ip) + "\"," + str(size) + "," + str(timeout))
        self.read_data(self.BASIC_TIMEOUT)
        start = time.time()
        while not self.comport.inWaiting():
            if time.time() - start > timeout + 0.500:
                print("No message has been received!")
                return

        data = self.read_data(self.BASIC_TIMEOUT)
        print(data)

        if "+NPINGERR:" in data:
            split_data = data.split(",")
            print(f"Ping request failure! ERROR: {data}")
            return

        if "+NPING:" in data:
            split_data = data.split(",")
            return [int(split_data[1]), int(split_data[2].strip("\r\n"))]

    def get_stats(self, stat_type):
        """Internal init function

        :param comport: serial port example: "COM15"
        :param speed: serial port baudrate speed example: 9600
        :return: None
        """
        
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
