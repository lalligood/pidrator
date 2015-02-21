#!/usr/bin/python

import time 
import RPi.GPIO as io 
io.setmode(io.BCM) 

power_pin = 23

io.setup(power_pin, io.OUT)
io.output(power_pin, False)

start_time = time.time()
main_cook = 600
keep_warm_on = 60
keep_warm_off = 240

print (start_time)
print("Main cook - POWER ON")
io.output(power_pin, True)
time.sleep(main_cook)
print (time.time)
print("Main cook - COMPLETE")
while True:
    print("POWER OFF")
    io.output(power_pin, False)
    time.sleep(keep_warm_off);
    print("POWER ON")
    io.output(power_pin, True)
    time.sleep(main_cook)
