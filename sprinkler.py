#!/usr/bin/python

import time
import RPi.GPIO as io

localtime = time.asctime()
print "Local current time :", localtime

RED = 23
io.setmode(io.BCM)
io.setup(RED, io.OUT) 

time.sleep(1) # trying to get all GPIO pins at LOW

if (localtime == 'Mon Oct 28 20:03:10 2013') :
    io.output(RED, io.HIGH) #switches on my green LED which will be a pump or valve

start_time = time.time()
elapsed_time = time.time() - start_time

# if elapsed_time == 3 min
io.output(RED, io.LOW)
