#!/usr/bin/python

import os	# needed for thermometer
import glob	# needed for thermometer
import time	# needed for thermometer & powertail
import RPi.GPIO as io	# needed for powertail
io.setmode(io.BCMo	# needed for powertail

power_pin = 23	# powertail data in

io.setup(power_pin, io.OUT)
io.output(power_pin, False)
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f

count = 0
header = 'Temp_C Temp_F Date_Time                Count'
while True:
# 5 lines below are for thermometer
    if count % 10 == 0:
	print header
    print '%4.3f %4.3f' % read_temp(), time.asctime(), count
    time.sleep(1)
    count += 1
# 6 lines below are for powertail switch
    print("POWER OFF")
    io.output(power_pin, False)
    time.sleep(30);
    print("POWER ON")
    io.output(power_pin, True)
    time.sleep(10)
