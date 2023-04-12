
from machine import UART
from machine import Pin
import time


class LoRaE5:
    """
        Construct a LoRaE5 class designed to control LoRa E5 HF module
    """
    def __init__(self, rx_pin, tx_pin, speed, debug=True):
        """
        Initialize a LoRaE5 class

        :param rx_pin: UART Rx pin
        :param tx_pin: UART Tx pin
        :param speed: UART Baud rate
        :param debug: controls the display of UART Tx Rx messages on stdout
        """
        self.RX_PIN = rx_pin
        self.TX_PIN = tx_pin
        self.SPEED = speed
        self.DEBUG = debug
        self.com = UART(1, baudrate=speed, tx=Pin(tx_pin), rx=Pin(rx_pin), timeout=200, timeout_char=5)

    def send_raw_command(self, command: str) -> None:
        """Send command directly to LoRaWAN module via UART

        :param command: AT command to transmit
        :return: None
        """
        if self.DEBUG:
            print('TX:\n{}'.format(command))
        self.com.write(command.encode() + b'\r\n')

    def read_data(self, multi: bool = False) -> str | None:
        """
        Read data received from module via UART

        :param multi: defines if multiple lines will be read
        :return: received data
        """
        resp = self.com.read()
        msg = ''
        try:
            msg = resp.decode('utf-8')
            if self.DEBUG:
                print('RX:\n{}'.format(msg))
        except Exception as e:
            if not multi:
                print(e.args)
        return msg

    def read_n_times(self, times: int) -> str:
        """
        Read from multiple lines responses from UART

        :param times: number or read repetitions total time defined by the *timeout* and *timeout_char*
        times from *UART* object
        :return: received data
        """
        ret = ''
        for i in range(times):
            msg = self.read_data(True)
            if len(msg) > 0:
                ret = ret + msg
            if 'Done' in msg:
                break
        return ret

    def test_at(self) -> str:
        """
        Used to test if connection of module is OK. This is a dummy command just like other common AT modules

        :return: received data
        """
        self.send_raw_command('AT')
        return self.read_data()

    def get_id(self) -> str:
        """
        Use to check the ID of the LoRaWAN module

        :return: module ID
        """
        self.send_raw_command('AT+ID')
        return self.read_data()

    def get_version(self) -> str:
        """
        Check firmware version

        :return: FW version
        """
        self.send_raw_command('AT+VER')
        return self.read_data()

    def set_id(self, mode: str, value: int) -> str | None:
        """
        Use to set the ID of the LoRaWAN module

        :param mode: ID to change DevAddr, DevEui, or AppEui
        :param value: ID value
        :return: new ID
        """
        if mode not in ['DevAddr', 'DevEui', 'AppEui']:
            print('Invalid parameter')
            return

        self.send_raw_command('AT+ID={},"{}"'.format(mode, value))
        time.sleep_ms(100)
        return self.read_data()

    def module_reset(self) -> str:
        """
        Use to reset LoRaWAN module

        :return: received data
        """
        self.send_raw_command('AT+RESET')
        time.sleep_ms(200)
        return self.read_data()

    def send_ascii(self, data: str, confirmed: bool = False) -> str:
        """
        Send LoRaWAN message in ASCII format

        :param data: data to send
        :param confirmed: confirmed/unconfirmed message
        :return: received data
        """
        if confirmed:
            self.send_raw_command('AT+CMSG={}'.format(data))
        else:
            self.send_raw_command('AT+MSG={}'.format(data))
        return self.read_data()

    def check_link(self) -> str:
        """
        Use to send LinkCheckReq mac command to check Link status between modem and server

        :return: link status
        """
        self.send_raw_command('AT+MSG')
        return self.read_data()

    def send_hex(self, data: str = None, confirmed: bool = False) -> str:
        """
        Send LoRaWAN message in HEX format

        :param data: data to send
        :param confirmed: confirmed/unconfirmed message
        :return: received data
        """
        part = 'MSGHEX'
        if confirmed:
            part = 'CMSGHEX'

        if data is None:
            self.send_raw_command('AT+{}'.format(part))
        else:
            self.send_raw_command('AT+{}="{}"'.format(part, data))
        return self.read_data()

    def get_port(self) -> str:
        """
        Get LoRaWAN port used for transmission

        :return: port
        """
        self.send_raw_command('AT+PORT=?')
        return self.read_data()

    def set_port(self, port: int) -> str | None:
        """
        Set LoRaWAN port

        :param port: numeric value from 0 to 255
        :return: new port
        """
        if not 0 <= port <= 255:
            print('Wrong port number')
            return

        self.send_raw_command('AT+PORT={}'.format(port))
        return self.read_data()

    def get_adr(self) -> str:
        """
        Get status of ADR

        :return: ADR status
        """
        self.send_raw_command('AT+ADR=?')
        return self.read_data()

    def set_adr(self, enable: bool = False) -> str:
        """
        Control ADR functionality

        :param enable: enable/disable
        :return: new ADR status
        """
        self.send_raw_command('AT+ADR={}'.format('ON' if enable else 'OFF'))
        return self.read_data()

    def get_dr(self) -> str:
        """
        Get current data rate

        :return: data rate
        """
        self.send_raw_command('AT+DR')
        return self.read_data()

    def set_dr(self, dr: int) -> str | None:
        """
        Set data rate value

        :param dr: data rate ranging from 0 to 15
        :return: new data rate value
        """
        if not 0 <= dr <= 15:
            print('Invalid DataRate')
            return
        self.send_raw_command('AT+DR={}'.format(dr))
        return self.read_data()

    def set_dr_band(self, band: str) -> str | None:
        """
        Set data rate scheme for current band (EU868)

        :param band: frequency band (currently only EU868 supported)
        :return: data rate plan
        """
        if band != 'EU868':
            print('Invalid Band')
            return
        self.send_raw_command('AT+DR={}'.format(band))
        return self.read_data()

    def get_band_scheme(self) -> str:
        """
        Get data rate scheme for current band (EU868)

        :return: data rate plan
        """
        self.send_raw_command('AT+DR=SCHEME')
        return self.read_data()

    def get_all_channels(self) -> str:
        """
        Query channels configuration

        :return: channels configuration
        """
        self.send_raw_command('AT+CH')
        return self.read_data()

    def get_channel(self, channel: int) -> str:
        """
        Get single channel configuration

        :param channel: channel value
        :return: channel configuration
        """
        self.send_raw_command('AT+CH={}'.format(channel))
        return self.read_data()

    def set_channel(self, channel: int, freq: int, drmin: int, drmax: int) -> str | None:
        """
        Set channel configuration

        :param channel: channel value
        :param freq: frequency
        :param drmin: minimum data rate
        :param drmax: maximum data rate
        :return: new channel configuration
        """
        if (not 0 <= drmin <= 15) or (drmin > drmax):
            print('Invalid DataRate')
            return
        if not 0 <= drmax <= 15:
            print('Invalid DataRate')
            return
        self.send_raw_command('AT+CH="{}",{},{},{}'.format(channel, freq, drmin, drmax))
        return self.read_data()

    def get_enabled_channels(self) -> str:
        """
        Get list of enabled channels

        :return: list of active channels
        """
        self.send_raw_command('AT+CH=NUM')
        return self.read_data()

    def enable_channel(self, channel: int) -> str:
        """
        Enable LoRaWAN channel

        :param channel: channel nuber
        :return: channel configuration
        """
        self.send_raw_command('AT+CH={},ON'.format(channel))
        return self.read_data()

    def disable_channel(self, channel: int) -> str:
        """
        Disable LoRaWAN channel

        :param channel: channel nuber
        :return: channel configuration
        """
        self.send_raw_command('AT+CH={},OFF'.format(channel))
        return self.read_data()

    def get_power(self) -> str:
        """
        Get TX power

        :return: TX power
        """
        self.send_raw_command('AT+POWER')
        return self.read_data()

    def set_power(self, power: int) -> str | None:
        """
        Set TX power

        :param power: power value
        :return: set TX power
        """
        if power > 14:
            print('Invalid Power Value')
            return
        self.send_raw_command('AT+POWER={}'.format(power))
        return self.read_data()

    def get_power_map(self) -> str:
        """
        Get TX power map

        :return: power map
        """
        self.send_raw_command('AT+POWER=TABLE')
        return self.read_data()

    def get_rep_limit(self) -> str:
        """
        Get maximum number of repetitions for unconfirmed messages

        :return: number of repetitions
        """
        self.send_raw_command('AT+REPT="Repeat Times"')
        return self.read_data()

    def set_rep_limit(self, rep: int) -> str | None:
        """
        Set maximum number of repetitions for unconfirmed messages

        :param rep: number of repetitions
        :return: set number of repetitions
        """
        if not 1 <= rep <= 15:
            print('Invalid RepNum')
            return
        self.send_raw_command('AT+REPT={}'.format(rep))
        return self.read_data()

    def get_ret_limit(self) -> str:
        """
        Get maximum number of retransmissions for confirmed message

        :return: number of retransmissions
        """
        self.send_raw_command('AT+RETRY="Retry Times"')
        return self.read_data()

    def set_ret_limit(self, ret: int) -> str | None:
        """
        Set maximum number of retransmissions for confirmed message

        :param ret: number of retransmissions
        :return: set number of retransmissions
        """
        if not 0 <= ret <= 254:
            print('Invalid RepNum')
            return
        self.send_raw_command('AT+RETRY={}'.format(ret))
        return self.read_data()

    def get_rx2(self) -> str:
        """
        Query RXWIN2 configuration

        :return: RXWIN2 configuration
        """
        self.send_raw_command('AT+RXWIN2')
        return self.read_data()

    def set_rx2(self, freq: int, dr: int) -> str | None:
        """
        Set RXWIN2 configuration

        :param freq: window frequency
        :param dr: data rate
        :return: RXWIN2 new configuration
        """
        if not 0 <= dr <= 15:
            print('Invalid DataRate')
            return
        self.send_raw_command('AT+RXWIN2={},DR{}'.format(freq, dr))
        return self.read_data()

    def set_key(self, key: str, value: int) -> str | None:
        """
        Set encryption keys

        :param key: type of key (NWKSKEY/APPSKEY/APPKEY)
        :param value: key value
        :return: newly set key
        """
        if key not in ['NWKSKEY', 'APPSKEY', 'APPKEY']:
            print('Invalid parameter')
            return

        self.send_raw_command('AT+KEY={},"{}"'.format(key, value))
        return self.read_data()

    def factory_reset(self) -> str:
        """
        Do factory reset

        :return: received data (OK)
        """
        self.send_raw_command('AT+FDEFAULT')
        return self.read_data()

    def set_mode(self, mode: str) -> str | None:
        """
        Set LoRaWAN operational mode

        :param mode: operational mode (TEST, LWOTAA, LWABP)
        :return: set mode
        """
        if mode not in ['TEST', 'LWOTAA', 'LWABP']:
            print('Invalid parameter')
            return

        self.send_raw_command('AT+MODE="{}"'.format(mode))
        return self.read_data()

    def set_counters(self, up: int, down: int) -> str:
        """
        Set uplink and downlink counter values

        :param up: uplink counter value
        :param down: downlink counter value
        :return: set value for both counters
        """
        self.send_raw_command('AT+LW=ULDL,{},{}'.format(up, down))
        return self.read_data()

    def get_counters(self) -> str:
        """
        Get uplink and downlink counter values

        :return: counters value
        """
        self.send_raw_command('AT+LW=ULDL')
        return self.read_data()

    def set_etsi_duty_cycle(self, enabled: bool = True) -> str:
        """
        Set ETSI defined duty cycle limitation

        :param enabled: enable/disable
        :return: duty cycle value
        """
        self.send_raw_command('AT+LW=DC, {}'.format('ON' if enabled else 'OFF'))
        return self.read_data()

    def set_duty_cycle(self, max_dc: int) -> str:
        """
        Set maximum duty cycle

        :param max_dc: duty cycle
        :return: duty cycle value
        """
        self.send_raw_command('AT+LW=DC, {}'.format(max_dc))
        return self.read_data()

    def get_rx_delay(self) -> str:
        """
        Get RX windows delay

        :return: RX windows delay
        """
        self.send_raw_command('AT+DELAY')
        return self.read_data()

    def set_rx_delay(self, window: str, delay: int) -> str | None:
        """
        Set RX windows delay

        :param window: RX window (RX1/RX2/JRX1/JRX2)
        :param delay: delay in ms
        :return: RX windows configuration
        """
        if window not in ['RX1', 'RX2', 'JRX1', 'JRX2']:
            print('Invalid parameter')
            return

        self.send_raw_command('AT+DELAY={}, {}'.format(window, delay))
        return self.read_data()
