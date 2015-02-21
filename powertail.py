#!/usr/bin/python

import time 
import RPi.GPIO as io 
io.setmode(io.BCM) 

power_pin = 23

io.setup(power_pin, io.OUT)
io.output(power_pin, False)

while True:
    print("POWER OFF")
    io.output(power_pin, False)
    time.sleep(30);
    print("POWER ON")
    io.output(power_pin, True)
    time.sleep(10)
