import machine
import time
from imu import MPU6050
import _thread

button = machine.Pin(35, machine.Pin.IN)

i2c = machine.I2C(0, sda=machine.Pin(21), scl=machine.Pin(22), freq=400000)
imu = MPU6050(i2c)

sLock = _thread.allocate_lock() 

button_pressed = False

last_time_but = 0
last_time_acc = 0
last_time_main = 0

last_ax = 0
last_ay =0
last_az = 0

i = 0


# ****** GPIO interrupt handler function ******
def button_pressed_handler(pin):
    global last_time_but
    new_time_but = time.ticks_ms()
    # if it has been more that 1/5 of a second since the last event, we have a new event
    if (new_time_but - last_time_but) > 200: 
        fun()
        last_time_but = new_time_but


button.irq(trigger=machine.Pin.IRQ_FALLING, handler = button_pressed_handler)

def fun():
    global i
    print("Hello " + str(i))
    i+=1

def CoreTask():
    global last_ax, last_ay, last_az, last_time_acc
    while True:
        #sLock.acquire()
        #print("Entered into the second Thred")
        new_ax=round(imu.accel.x,2)
        new_ay=round(imu.accel.y,2)
        new_az=round(imu.accel.z,2)

        if new_ax != last_ax or new_ay != last_ay or new_az != last_az:
            new_time_acc = time.ticks_ms()
            if last_time_acc == 0:
                new_time_acc += 55000
            if (new_time_acc - last_time_acc) > 60000:
                print("Values changed")
                if last_time_main == 0:
                    last_time_acc = (new_time_acc - 55000)    
                last_time_acc = new_time_acc
        last_ax = new_ax
        last_ay = new_ay
        last_az = new_az

        #print("Exiting from the 2nd Thread")
        time.sleep(1)
        #sLock.release()
_thread.start_new_thread(CoreTask, ())

while(1):
    #sLock.acquire()
    #print("Entered into the main Thred")
    fun()
    new_time_main = time.ticks_ms()
    time.sleep(120)
    #print("Exiting from the main Thread")
    #sLock.release()