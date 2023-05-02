from machine import Pin, SPI
import sdcard
import os

# Initialise SPI used by SD
# SD   | GP
# ----------
# SCK  | 10
# MOSI | 11
# MISO | 12
# CS   | 9
# ----------
sd_spi = SPI(1, sck = Pin(10, Pin.OUT), mosi = Pin(11, Pin.OUT),
             miso = Pin(12, Pin.OUT))
# Create SDCard object
sd = sdcard.SDCard(sd_spi, Pin(9, Pin.OUT))

# Mount SD card to /SD folder (doesn't have to exist beforehand)

os.mount(sd, "/SD")
print("Mounted")
# Print SD card size
print("Size: {} MB".format(sd.sectors/2048))
# List SD contents
print(os.listdir("/SD"))
print(os.listdir())

"""
# Create a file in write mode and write something
with open("/sd/sdtest.txt", "w") as file:
    file.write("Hello World!\r\n")
    file.write("This is a test\r\n")
"""
"""
# Create a file in write mode and write something
with open("/SD/GPS_test.txt", "w") as file:
    file.write("test lat:\r\n")
    file.write("test lon:\r\n")
"""
# Open the file in read mode and read from it
with open("/SD/GPS_test.txt", "r") as file:
    data = file.read()
    print(data)
    
os.umount("/SD")