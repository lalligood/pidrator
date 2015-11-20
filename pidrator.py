#!/usr/bin/python3
__author__ = 'lalligood'

import core as c
from datetime import datetime, timedelta
import glob
import logging
import os
import time

'''
**** PARAMETERS ****
'''

# For inserting dates to DB & for logging
date_format = '%Y-%m-%d %H:%M:%S' # YYYY-MM-DD HH:MM:SS
# Logging information
logfilename = 'pidrator.log'
loglevel = logging.WARNING # Available logging levels, from low to high: DEBUG, INFO, WARNING, ERROR, CRITICAL
logformat = '%(asctime)s [%(levelname)s] %(message)s'
logging.basicConfig(filename=logfilename, level=loglevel, format=logformat, datefmt=date_format)
logging.info('Initializing application & attempting to connect to database.')
# Hardware configuration
power_pin = 23 # GPIO pin 23

'''
**** MAIN ROUTINE ****
'''
def main():
    '''This is the main routine for controlling the cooking device with a
    Raspberry Pi. All cooking data is stored in a PostgreSQL database.

    Before running this application, you should run buildtables.py to set up the
    database.'''
    # Make sure running on python 3.x
    c.python_ver()

    # Enable all hardware attached to RaspPi
    c.enablepihw()

    # Open connection to database
    thedb = c.DBconn()

    # User login
    user = c.loginmenu(thedb)
    print('\n\n')

    # User password change (optional)
    c.changepswdprompt(thedb, user)

    # Pick job from list
    jobname = c.picklist(thedb, 'job names', 'jobname', 'job_info', 'createtime')
    jobid = thedb.query('select id from job_info where jobname = (%s)',
        jobname, False, 'one')
    print('\n\n')

    # Pick cooking device from list
    devname = c.picklist(thedb, 'cooking devices', 'devicename', 'devices', 'devicename')
    deviceid = thedb.query('select id from devices where devicename = (%s)',
        devname, False, 'one')
    print('\n\n')

    # Pick food from list
    foodname = c.picklist(thedb, 'foods', 'foodname', 'foods', 'foodname')
    foodid = thedb.query('select id from foods where foodname = (%s)',
        foodname, False, 'one')
    print('\n\n')

    # Get user_id
    userid = thedb.query('select id from users where username = (%s)',
        user, False, 'one')

    # Get temperature setting
    tempcheck = thedb.query('select temperature from job_info where id = (%s)',
        jobid, False, 'one')
    if tempcheck[0] == None: # No previous cooking data available
        print('No previous temperature found.')
        tempset = c.dbinput('What temperature (degrees or setting) are you going to cook your job at? ', '')
    else: # Previous cooking data available
        while True: # Will food will be cooked at same temp as last time?
            print('Last job was cooked at temperature/setting: {}.'.format(tempcheck[0]))
            response = input('Are you going to cook at the same temperature/setting? [Y/N] ')
            if response.lower() == 'y': # Cook at the same temp
                print('You selected to cook at the same temperature/setting.')
                tempset = tempcheck
                break
            elif response.lower() == 'n': # Cook at a different temp
                tempset = c.dbinput('What temperature/setting are you going to use this time? ', '')
                break
            else:
                c.errmsgslow('Invalid selection. Please try again...')
    print('\n\n')

    # Update user_id, device_id, & food_id in job_info
    thedb.query('''update job_info set user_id = (%s), device_id = (%s),
        food_id = (%s), temperature = (%s) where id = (%s)''',
        userid + deviceid + foodid + tempset + jobid, True)

    # Now make sure it worked...!
    row = thedb.query('''select
            jobname
            , users.fullname
            , devices.devicename
            , foods.foodname
            , temperature
        from job_info
            left outer join users on job_info.user_id = users.id
            left outer join devices on job_info.device_id = devices.id
            left outer join foods on job_info.food_id = foods.id
        where jobname = (%s)''', jobname, False, 'one')
    # Convert tuple to list
    list(row)
    print('\n\n')
    print('\tJob name:            {}'.format(row[0]))
    print('\tPrepared by:         {}'.format(row[1]))
    print('\tCooking device:      {}'.format(row[2]))
    print('\tFood being prepared: {}'.format(row[3]))
    print('\tAt temperature:      {}'.format(row[4]))
    print('\n\n')

    c.getjobtime()
    c.confirmjob()

    # Update job_info row with start time
    start = datetime.now()
    starttime = c.dbdate(start)
    thedb.query('update job_info set starttime = (%s) where id = (%s)',
        starttime + jobid, True)

    # Calculate job run time
    cookdelta = timedelta(hours=cookhour, minutes=cookmin)
    cooktime = c.dbnumber((cookhour * 60) + cookmin)
    end = start + cookdelta
    endtime = c.dbdate(end)
    thedb.query('''update job_info set endtime = (%s), cookminutes = (%s)
        where id = (%s)''', endtime + cooktime + jobid, True)
    print('''Your job is going to cook for {} hour(s) and {} minute(s).
        It will complete at {}.'''.format(cookhour, cookmin, endtime[0]))

        # Main cooking loop
    fractmin = 15 # After how many seconds should I log temp to database?
    currdelta = timedelta(seconds=fractmin) # How often it should log data while cooking
    countdown = 0
    if raspi:
        c.powertail(True)
    while True:
        currtime = datetime.now()
        if currtime >= start + currdelta:
            current = c.dbdate(currtime)
            if raspi and therm_sens: # If running RPi & thermal sensor is present
                temp_cen, temp_far = c.gettemp() # Read temperature
                temp_c = c.dbnumber(temp_cen) # Convert to tuple
                temp_f = c.dbnumber(temp_far) # Convert to tuple
                thedb.query('''insert into job_data
                    (job_id, moment, temp_c, temp_f)
                    values ((%s), (%s), (%s))''',
                    jobid + current + temp_c + temp_f, True)
            else: # If running on test, then don't read temperature
                thedb.query('''insert into job_data (job_id, moment)
                    values ((%s), (%s), (%s))''', jobid + current, True)
            start = datetime.now()
            countdown += (fractmin / 60)
            timeleft = int(cooktime[0]) - countdown
            if raspi and therm_sens:
                print('Job has been active for {} minutes.'.format(countdown))
                print('There are {} minutes left.'.format(timeleft))
                print('The current temperature is {} degrees C.'.format(temp_cen))
            else:
                print('Job has been active for {} minutes and there are {} minutes left.'.format(countdown, timeleft))
        if raspi and currtime >= end: # Powertail off & stop if RasPi
            c.powertail(False)
            break
        elif currtime >= end: # Otherwise stop when time has ended
            break

    print('\n\n')
    print('Job complete!')
    c.cleanexit(0)

if __name__ == "__main__":
    main()
