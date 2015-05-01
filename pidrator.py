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


def selectDeviceMenu():
    while True:
        #os.system('clear') # clear screen
        print """Welcome to pidrator
    1. Dehydrator
    2. Slow Cooker"""
        try:
            cookdevice = int(raw_input('Enter the number (1 - 2) of the device you want to control: '))
            if cookdevice == 1:
                print 'Dehydrator selected.'
            elif cookdevice == 2:
                print 'Slow cooker selected.'
        except ValueError:
            print 'That is not a valid selection. Please try again...'
            continue

        #if not cookdevice in range(1, 3):
            #print 'That is not a valid selection. Please try again...'
            #continue
        return cookdevice

def selectFoodMenu():
    while True:
        try:
            cookfood = str(raw_input('What are you planning to cook? '))
            if len(cookfood) < 5:
                print 'You must enter a useful description. Please try again...'
                continue
        except ValueError:
            print 'You must enter a useful description. Please try again...'
            continue
        return cookfood

def selectTimeMenu():
    while True:
        try:
            cookhour = int(raw_input('Enter the number of hours would you like to cook: '))
            if cookhour in range(2, 13):
                print 'You want to cook something for', cookhour, 'hours.'
        except ValueError:
            print 'The time entered is too short or too long. Please try again...'
            continue

        if not cookhour in range(2, 13):
            print 'The time entered is too short or too long. Please try again...'
            continue
        return cookhour


# Configure logging
logfilename = 'pidrator.log'
loglevel = logging.DEBUG
logformat = '%(asctime)s %(levelname)s: %(message)s'
logdateformat = '%Y-%m-%d %I:%M:%S%p'
logging.basicConfig(filename=logfilename, level=loglevel, format=logformat, datefmt=logdateformat)

# Main routine
logging.info('Starting up pidrator engine.')
enable()
selectDeviceMenu()
selectFoodMenu()
selectTimeMenu()
print "You are planning to use the", cookdevice, "to make", cookfood, "for ", cookhour, "hours."
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