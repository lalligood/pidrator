#!/usr/bin/python3
__author__ = 'lalligood'

import core as c
import glob
import logging
import os
import platform
# Enable some functionality ONLY if raspi!
raspi = platform.machine().startswith('armv')
if raspi:
    from RPi import GPIO

'''
**** PARAMETERS ****
'''

# For inserting dates to DB & for logging
date_format = '%Y-%m-%d %H:%M:%S' # YYYY-MM-DD HH:MM:SS
# Logging information
logfilename = 'buildtables.log'
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
    '''Main routine connects to database, checks to see if all necessary
extensions are loaded, and that all tables exist. Otherwise it will attempt to
create any missing extensions or tables in the database.'''
    # Verify running python 3.x
    c.python_ver()

    # Open connection to database
    thedb = c.DBconn()

    # Verify database extensions have been installed
    c.verify_pgextensions(thedb)

    # Check to see if all tables exists
    schema = ('public', )
    tables = thedb.query('''select table_name from information_schema.tables
        where table_schema = (%s) order by table_name''', schema, False, 'all')
    tables_list = [] # Convert results tuple -> list
    for table in tables:
        print(table[0] + ' table found.')
        tables_list.append(table[0])
    master_list = ['devices', 'foodcomments', 'foods', 'job_data', 'job_info', 'users']
    # Get difference of master_list & tables_list
    results_list = set(master_list).difference(tables_list)
    if len(results_list) > 0:
        # Create any missing table(s) in the database
        for result in results_list:
            options = {
                'devices' : c.create_devices,
                'foodcomments' : c.create_foodcomments,
                'foods' : c.create_foods,
                'job_data' : c.create_job_data,
                'job_info' : c.create_job_info,
                'users' : c.create_users,
                }
            options[result](thedb)
    else:
        print('\nConfirmed that all tables present & accounted for. Exiting...')
    thedb.cleanexit(0)

if __name__ == "__main__":
    main()
