#!/usr/bin/python3
__author__ = 'lalligood'

import core as c
import logging

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

if __name__ == "__main__":
    main()
