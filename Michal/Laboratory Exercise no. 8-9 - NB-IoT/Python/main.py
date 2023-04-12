import time

from modules.nbiot import NBIoT

COMPORT = "COM11"
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
 
    nb.is_operator_set(OPERATOR)
    nb.is_attached()
    
    nb.open_socket(65006)
    nb.send_message("Dobry den vitame vas u pripojeni k siti", "147.229.146.40", "65006", "0x200", "0")
    nb.get_stats("RADIO")
    nb.get_stats("CELL")
    nb.wait_for_message(1000)
    nb.read_message(0, 256)
    nb.get_stats("RADIO")
    nb.get_stats("CELL")
    nb.ping_to_remote("147.229.146.40",1000,50000)
    print("aktivni rezim")
    nb.enable_psm("00011000", "00111011") #aktivni rezim a rezim spanku nastavujeme za pmoci 8 bitoveho binarniho cisla.  
    print("rezim spanku")
    
    
   

if __name__ == "__main__":
    main()