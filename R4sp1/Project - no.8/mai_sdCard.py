from machine import Pin, SPI
import sdcard
import os

# Initialize the SD card
spi=SPI(1,baudrate=0x14<<20,sck=Pin(10),mosi=Pin(11),miso=Pin(12))
sd=sdcard.SDCard(spi,Pin(9))

# Create a instance of MicroPython Unix-like Virtual File System (VFS),
vfs=os.VfsFat(sd)
 
# Mount the SD card
os.mount(sd,'/sd')
# Debug print SD card directory and files
print(os.listdir('/sd'))

# Create / Open a file in write mode.
# Write mode creates a new file.
# If  already file exists. Then, it overwrites the file.
file = open("/sd/sample.txt","w")
# Write sample text
for i in range(20):
    file.write("Sample text = %s\r\n" % i)
    
# Close the file
file.close()
# Again, open the file in "append mode" for appending a line
file = open("/sd/sample.txt","a")
file.write("Appended Sample Text at the END \n")
file.close()
# Open the file in "read mode". 
# Read the file and print the text on debug port.
file = open("/sd2/sample.txt", "r")
if file != 0:
    print("Reading from SD card")
    read_data = file.read()
    print (read_data)
file.close()
# Initialize timer_one. Used for toggling the on board LED
timer_one = machine.Timer()
# Timer one initialization for on board blinking LED at 200mS interval
timer_one.init(freq=5, mode=machine.Timer.PERIODIC, callback=BlinkLED)