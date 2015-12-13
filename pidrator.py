#!/usr/bin/python3

'''pidrator is a designed to be run on a Raspberry Pi (any model) to control and
monitor the progress of a slow cooker or food dehydrator. All data collected
before & during the cooking procedure is logged to a PostgreSQL database.

This project is stored and maintained at
    https://gitlab.com/lalligood/pidrator'''

__author__ = 'Lance Alligood'
__email__ = 'lalligood@gmail.com'
#__version__ = 'TBD'
__status__ = 'Prototype'

import core as c
import logging

'''
**** PARAMETERS ****
'''

# For inserting dates to DB & for logging
date_format = '%Y-%m-%d %H:%M:%S' # YYYY-MM-DD HH:MM:SS
# Logging information
logfilename = 'app-pidrator.log'
loglevel = logging.ERROR # Available logging levels, from low to high: DEBUG, INFO, WARNING, ERROR, CRITICAL
logformat = '%(asctime)s [%(levelname)s] %(message)s'
logging.basicConfig(filename=logfilename, level=loglevel, format=logformat, datefmt=date_format)
logging.info('Initializing application & attempting to connect to database.')

'''
**** MAIN ROUTINE ****
'''

def main():
    '''This is the main routine for controlling the cooking device with a
    Raspberry Pi. All cooking data is stored in a PostgreSQL database.

    The first time you run pidrator, you need to build the necessary tables and
    extensions (menu option) and create a user (menu option).'''
    # Make sure running on python 3.x
    c.verify_python_version()
    # Open connection to database
    thedb = c.RasPiDatabase()
    # Main menu
    while True:
        user = thedb.main_menu()

if __name__ == "__main__":
    main()
