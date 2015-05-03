1#!/usr/bin/python
__author__ = 'lalligood'

import os
import glob
import logging
import sys
import time
try:
    import RPi.GPIO as io
except RuntimeError:
    print("Error Importing RPi.GPIO!")

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
    # Configure powertail
    #io.setmode(io.BCM)
    #io.setup(powertail['power_pin'], io.OUT)
    #io.output(powertail['power_pin'], False)
    # Configure thermometer & begin data collection
    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')
    base_dir = '/sys/bus/w1/devices/'
    #device_folder = glob.glob(base_dir + '28*')[0]
    #device_file = device_folder + '/w1_slave'
    device_file = False # This added to ensure following condition is false
    if device_file:
        msg = 'Thermometer detected & started successfully.'
    else:
        msg = 'Thermometer not found.'
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
                menu['device'] = 'dehydrator'
            elif cookdevice == 2:
                print 'Slow cooker selected.'
                menu['device'] = 'slow cooker'
        except ValueError:
            print 'That is not a valid selection. Please try again...'
            continue

        if not cookdevice in range(1, 3):
            print 'That is not a valid selection. Please try again...'
            continue
        return menu

def selectFoodMenu():
    while True:
        try:
            cookfood = str(raw_input('What are you planning to cook? '))
            if len(cookfood) < 5:
                print 'You must enter a useful description. Please try again...'
                continue
            else:
                menu['food'] = cookfood
        except ValueError:
            print 'You must enter a useful description. Please try again...'
            continue
        return menu

def selectTimeMenu():
    while True:
        try:
            cookhour = int(raw_input('Enter the number of hours would you like to cook: '))
            if cookhour in range(2, 13):
                menu['hour'] = cookhour
        except ValueError:
            print 'The time entered is too short or too long. Please try again...'
            continue

        if not cookhour in range(2, 13):
            print 'The time entered is too short or too long. Please try again...'
            continue
        return menu


# Configure logging
logfilename = 'pidrator.log'
loglevel = logging.DEBUG
logformat = '%(asctime)s %(levelname)s: %(message)s'
logdateformat = '%Y-%m-%d %I:%M:%S%p'
logging.basicConfig(filename=logfilename, level=loglevel, format=logformat, datefmt=logdateformat)

# Main routine
print "Current date/time is:", time.asctime()
logging.info('Starting up pidrator engine.')
powertail = {
    'power_pin': 23	# powertail data in
}
enable()
menu = {}
selectDeviceMenu()
selectFoodMenu()
selectTimeMenu()
print "You want to cook", menu['food'], "in the", menu['device'], "for", menu['hour'], "hours."
count = 0
while True:
    if count % 10 == 0:
        print "Temp F  Temp C  Time           Count"
    #print '%4.3f %4.3f' % read_temp(), time.asctime(), count
    count += 1
    poweron()
    userwait()
    poweroff()
    userwait()
    if count == 2:
        break

msg = 'Shutting down pidrator engine.'
logging.info(msg)
print msg
userquit()