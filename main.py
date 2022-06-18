from machine import Timer, Pin
from time import sleep, time, ticks_us, ticks_diff
import os
import ujson

from mpu import MPU6050
from pulse import HeartRate
from ble import ESP32_BLE

ACCEL_RANGE_2G = 0x00
ACCEL_RANGE_4G = 0x08
ACCEL_RANGE_8G = 0x10
ACCEL_RANGE_16G = 0x18

led = Pin(23,Pin.OUT)
timer0 = Timer(0)

def handle_tmr0(timer):
    global flag_tmr0
    flag_tmr0 = True
    
def encap_data(idx,t_set,hr_set,time_set, z_set):
    _id = str(ble.name) + ":" + str(idx)
    msg1 = {
        "id":str(_id),
        "th":t_set,
        "tm":time_set
        }
    msg2 = {
        "id":str(_id),
        "hr_value":hr_set,
        "motion_value":z_set
        }
 
    return msg1, msg2
    

# def encap_data(idx,t_set,hr_set,time_set, z_set):
#     _id = str(ble.name) + ":" + str(idx)
#     msg = {
#         "id":str(_id),
#         "hr":{
#             "time":t_set,
#             "value":hr_set
#         },
#         "motion":{
#             "time":time_set,
#             "value":z_set
#         }
#     }
#     msg = ujson.dumps(str(msg))
#     return msg



'''init timer'''
timer0.init(period=10, mode = Timer.PERIODIC, callback=handle_tmr0)
flag_tmr0 = False

'''init BLE'''
# random_num = int.from_bytes(os.urandom(3), 'little')
client_name = 'ESP32_Lam_Loc'
ble = ESP32_BLE(client_name)

'''init mpu'''
pulseS = HeartRate(34)
accel = MPU6050(18, 19, ACCEL_RANGE_2G)

count_time  = 0
z_set = []
time_set = []
timer = 0
curr_time = 0
last_time = 0

hr_set = []
t_set = []
t = 0
curr_t = 0
last_t = 0

index = 0

flag_collect = 0

while True:
    
    while not flag_tmr0:
        pass
    flag_tmr0 = False
    
    if ble.ble_msg == 'Disconnect':
        ble.ble_msg = ""
        ble.ble_irq(2,"")
        
    elif ble.ble_msg == 'Start':
        ble.ble_msg = ""
        flag_collect = 1
        
    elif ble.ble_msg == 'Stop':
        ble.ble_msg = ""
        flag_collect = 0
        
    if ble.connection_stt == False:
        if count_time % 10 == 0:
            led.value(not led.value())
        count_time += 1
        
        z_set = []
        time_set = []
        timer = 0
        curr_time = 0
        last_time = 0

        count = 0

        hr_set = []
        t_set = []
        t = 0
        curr_t = 0
        last_t = 0

        index = 0
        
    else:
        
        if count_time % 50 == 0:
            led.value(not led.value())
        

            
        #if flag_collect == 1:
        
        if count_time > 200:
            count_time = 0
    
        if count_time == 200:
            msg1, msg2 = encap_data(index,t_set,hr_set,time_set, z_set)
#             print(msg1)
#             print(msg2)
            try:
                ble.send(str(msg1))
            except:
                pass
            else:
                try:
                    ble.send(str(msg2))
                except:
                    pass
            print(hr_set)
            count_time = 0
            index += 1
            t_set = []
            hr_set = []
            time_set = []
            z_set = []
        
        try:  
            hr = pulseS.get_hr()
        except:
            pass
        else:
            if (hr != None):
                curr_t = ticks_us()
                if last_t != 0:
                    t = t + ticks_diff(curr_t, last_t)/1000000
                else:
                    t = 0
                last_t = curr_t
                hr_set.append(str(hr))
                t_set.append([str(int(t)),str(int((t - int(t))*1000000))])
        
        if count_time % 10 == 0:
        
            try:
                z = accel.get_accel_z_value(True)
            except:
                pass
            else:
                curr_time = ticks_us()
                if last_time != 0:
                    timer = timer + ticks_diff(curr_time, last_time)/1000000
                else:
                    timer = 0
                last_time = curr_time
                z_set.append(str(z))
                time_set.append([str(int(timer)),str(int((timer - int(timer))*1000000))])
            
        count_time += 1