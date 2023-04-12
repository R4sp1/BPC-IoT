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
    nb.set_status_report(NBIoT.REPORT_CONNECTION_STATUS,0)
    nb.enable_psm("00001000","00011011")

    while not nb.is_attached():
        time.sleep(1)
    nb.open_socket(65008)
    nb.send_message("i0oUTUGyWootUqlDazs63TIr2xtsX54hIg9lGnWk3RMA1cRbn7JQwP9oIVULBlP3","147.229.146.40",65008,NBIoT.FLAG_200,0)
    start = time.time()
    #nb.wait_for_report(NBIoT.REPORT_CONNECTION_STATUS,1000)
    #nb.ping_to_remote("147.229.146.40", 12, 20000)
    
    #time.sleep(1)
    #nb.send_message("ahoj","147.229.146.40",65008,NBIoT.FLAG_000,0)
    #time.sleep(1)
    #nb.set_status_report(NBIoT.REPORT_PSM,1)
    #nb.wait_for_report(NBIoT.REPORT_PSM,100)
    
    nb.wait_for_message(10000)
    end = time.time()
    nb.read_message(0,64)
    print("Time from send to recive: ", end-start)
    #nb.wait_for_report(NBIoT.REPORT_CONNECTION_STATUS,1000)
    
    #nb.get_stats(NBIoT.NUESTATS_RADIO)
    
    
if __name__ == "__main__":
    main()