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
logfilename = 'app-pidrator.log'
loglevel = logging.WARNING # Available logging levels, from low to high: DEBUG, INFO, WARNING, ERROR, CRITICAL
logformat = '%(asctime)s [%(levelname)s] %(message)s'
logging.basicConfig(filename=logfilename, level=loglevel, format=logformat, datefmt=date_format)
logging.info('Initializing application & attempting to connect to database.')

'''
**** MAIN ROUTINE ****
'''
def main():
    '''This is the main routine for controlling the cooking device with a
    Raspberry Pi. All cooking data is stored in a PostgreSQL database.

    Before running this application, you should run buildtables.py to set up the
    database.'''
    # Make sure running on python 3.x
    c.verify_python_version()

    # Open connection to database
    thedb = c.RasPiDatabase()

    while True:
        # Main menu
        user = thedb.main_menu()

        # Pick food from list
        foodid = c.pick_list(thedb, 'foods', 'foodname', 'foods', 'foodname')

        # Pick cooking device from list
        deviceid = c.pick_list(thedb, 'cooking devices', 'devicename',
            'devices', 'devicename')

        # Pick job from list
        jobid = c.pick_list(thedb, 'job names', 'jobname', 'job_info',
            'createtime')

        # Get user_id
        userid = thedb.query('select id from users where username = (%s)',
            user, False, 'one')

        # Get temperature setting
        tempset = thedb.get_temp_setting(jobid)

        # Update user_id, device_id, & food_id in job_info
        thedb.query('''update job_info set user_id = (%s), device_id = (%s),
            food_id = (%s), temperature = (%s) where id = (%s)''',
            userid + deviceid + foodid + tempset + jobid, True)

        # Now make sure it worked...!
        thedb.describe_job(jobid)
        c.get_job_time()
        thedb.confirm_job()

        # Set job start time
        thedb.set_job_start_time(jobid)

        # Calculate job run time
        thedb.calculate_job_time(jobid)

        # Main cooking loop
        fractmin = 15 # Log temp to database in seconds
        currdelta = timedelta(seconds=fractmin)
        countdown = 0
        thedb.powertail(True) # Turn Powertail on
        while True:
            currtime = datetime.now()
            if currtime >= start + currdelta:
                current = c.dbdate(currtime)
                if raspi and therm_sens:
                    temp_cen, temp_far = c.get_temp() # Read temperature
                    temp_c = c.dbnumber(temp_cen)
                    temp_f = c.dbnumber(temp_far)
                    thedb.query('''insert into job_data
                        (job_id, moment, temp_c, temp_f)
                        values ((%s), (%s), (%s))''',
                        jobid + current + temp_c + temp_f, True)
                else: # If running on test, then don't read temperature
                    thedb.query('''insert into job_data (job_id, moment)
                        values ((%s), (%s))''', jobid + current, True)
                start = datetime.now()
                countdown += (fractmin / 60)
                timeleft = int(cooktime[0]) - countdown
                if raspi and therm_sens:
                    print('Job has been active for {} minutes.'.format(countdown))
                    print('There are {} minutes left.'.format(timeleft))
                    print('The current temperature is {} degrees C.'.format(temp_cen))
                else:
                    print('Job has been active for {} minutes and there are {} minutes left.'.format(countdown, timeleft))
            # Quit when job has completed
            if currtime >= end: # Otherwise stop when time has ended
                thedb.powertail(False) # Turn Powertail off
                print('\n\n')
                print('Job complete!')
                break


if __name__ == "__main__":
    main()
