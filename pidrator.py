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
        foodid = thedb.pick_list('foods', 'foodname', 'foods', 'foodname')

        # Pick cooking device from list
        deviceid = thedb.pick_list('cooking devices', 'devicename',
            'devices', 'devicename')

        # Pick job from list
        jobid = thedb.pick_list('job names', 'jobname', 'job_info',
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
        finish_time = thedb.calculate_job_time(jobid)

        # Main cooking loop
        main_cooking_loop(jobid, finish_time)

if __name__ == "__main__":
    main()
