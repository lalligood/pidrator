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
    c.verify_python_version()

    # Open connection to database
    thedb = c.DBconn()

    # Verify database extensions have been installed
    c.verify_pgextensions(thedb)

    # Verify database tables exist or create them if they do not
    c.verify_schema(thedb)

    thedb.clean_exit(0)

if __name__ == "__main__":
    main()
