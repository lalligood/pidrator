#!/usr/bin/python
__author__ = 'lalligood'

import os
import glob
import logging
import sys
import time
#import RPi.GPIO as io

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


def userquit():
    msg = "Terminating pidrator."
    logging.warning(msg)
    print msg
    sys.exit(0)


def userwait():
    time.sleep(5)


def enable():
    # Configure powertail & begin data collection
    #io.setmode(io.BCM)
    power_pin = 23	# powertail data in
    #io.setup(power_pin, io.OUT)
    #io.output(power_pin, False)
    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')
    base_dir = '/sys/bus/w1/devices/'
    #device_folder = glob.glob(base_dir + '28*')[0]
    #device_file = device_folder + '/w1_slave'
    device_file = False # This added to ensure following condition is false
    if device_file:
        msg = 'Powertail detected & started successfully.'
    else:
        msg = 'Powertail not found.'
    logging.info(msg)
    print msg


def poweron():
    #io.output(power_pin, True)
    msg = 'Powertail turned ON successfully.'
    logging.info(msg)
    print msg


def poweroff():
    #io.output(power_pin, False)
    msg = 'Powertail turned OFF successfully.'
    logging.info(msg)
    print msg


def selectmenu():
    #os.system('clear') # clear screen
    print 'Welcome to pidrator'
    print '1. Dehydrator'
    print '2. Slow Cooker'
    cookdevice = int(raw_input('Enter the number of the device you want to cook with: '))
    if cookdevice == 1:
        print 'You selected Dehydrator.'
    elif cookdevice == 2:
        print 'You selected Slow Cooker.'
    else:
        print 'That is not a valid selection. Please try again...'
        time.sleep(5)
        selectmenu()
    cookfood = raw_input('What are you planning to cook? ')
    if cookfood == '':
        print 'Please enter what you are planning to cook...'
        time.sleep(5)
        selectmenu()
    cookhour = int(raw_input('Enter the number of hours would you like to cook: '))
    if cookhour > 2 or cookhour <= 12:
        print 'You want to cook something for', cookhour, 'hours.'
    else:
        print 'You have entered a time that is too short or too long. Please try again...'
        time.sleep(5)
        selectmenu()


# Configure logging
logfilename = 'pidrator.log'
loglevel = logging.DEBUG
logformat = '%(asctime)s %(levelname)s: %(message)s'
logdateformat = '%Y-%m-%d %I:%M:%S%p'
logging.basicConfig(filename=logfilename, level=loglevel, format=logformat, datefmt=logdateformat)

# Main routine
logging.info('Starting up pidrator engine.')
enable()
selectmenu()
count = 0
header = 'Temp_C Temp_F Date_Time                Count'
while True:
    if count % 10 == 0:
        print header
    #print '%4.3f %4.3f' % read_temp(), time.asctime(), count
    count += 1
    poweron()
    userwait()
    poweroff()
    if count == 2:
        break

msg = 'Shutting down pidrator engine.'
logging.info(msg)
print msg
userquit()