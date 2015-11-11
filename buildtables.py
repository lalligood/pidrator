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
    '''Main routine for connecting to database, checking to see if all necessary
extensions are loaded & all tables exist, otherwise create any/all that are
missing.'''
    # Verify running python 3.x
    c.python_ver()

    # Open connection to database
    thedb = c.DBconn()

    # Check to see if all tables exists
    schema = ('public', )
    tables = thedb.query('''select table_name from information_schema.tables
        where table_schema = (%s) order by table_name''', schema, False, 'all')
    tables_list = [] # Convert results tuple -> list
    for table in tables:
        tables_list.append(table[0])
    master_list = ['devices', 'foodcomments', 'foods', 'job_data', 'job_info', 'users']
    # Get difference of master_list & tables_list
    results_list = set(master_list).difference(tables_list)
    # Create any tables that do not exist
    if len(results_list) > 0:
        try:
            thedb.query('create extension if not exists "uuid-ossp";')
            thedb.query('create extension if not exists "pgcrypto";')
        except psycopg2.Error as dberror:
            logging.critical("Unable to create PostgreSQL extensions. Run 'apt-get install postgresql-contrib-9.4'.")
            logging.critical("Then re-run buildtables.py.")
            c.cleanexit(1)
        for result in results_list:
            options = {
                'devices' : c.create_devices,
                'foodcomments' : c.create_foodcomments,
                'foods' : c.create_foods,
                'job_data' : c.create_job_data,
                'job_info' : c.create_job_info,
                'users' : c.create_users,
                }
            options[result]()
    else:
        print('Confirmed that all tables present & accounted for. Exiting...')
    c.cleanexit(0)

if __name__ == "__main__":
    main()
