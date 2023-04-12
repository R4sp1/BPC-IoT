import time

from modules.nbiot import NBIoT

COMPORT = "COM17"
SPEED = 9600
OPERATOR = "23003"
APN = "lpwa.vodafone.iot"

def main():
    nb = NBIoT(COMPORT, SPEED)
    nb.reboot_module()
    nb.set_band(NBIoT.BAND_20)
    nb.set_power_class(NBIoT.POWER_CLASS_3, NBIoT.BAND_20)
    nb.switch_radio(1)
    nb.set_apn_name(APN)
    nb.set_operator(OPERATOR)

    while not nb.is_attached():
        time.sleep(1)
    nb.set_status_report(NBIoT.REPORT_PSM, 1)
    nb.open_socket(65008)
    #nb.send_message("ahoj","147.229.146.40",65008,NBIoT.FLAG_200,0)
    nb.ping_to_remote("147.229.146.40", 12, 20000)
    nb.enable_psm(00000000,00000000)
    
    #nb.wait_for_message(1000)
    #nb.read_message(0,12)
    nb.get_stats(NBIoT.NUESTATS_RADIO)
    
    
if __name__ == "__main__":
    main()