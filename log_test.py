#!/usr/bin/python
# pidrator.py
__author__ = 'lalligood'
# This is designed to use the Raspberry Pi, PowerTail, & thermal
# sensor to control either a food dehydrator or slow cooker.
# Aside from taking user input when ready to cook something,
# it will store information in a PostgreSQL database & serve
# up information about the jobs executed to a webpage.

import sys
import time
# https://docs.python.org/2/howto/logging.html
import logging
#import psycopg2 as pg2 # Not used yet -- for read/write to postgres

def userquit():
    print "Terminating at user request."
    sys.exit(0)

def userwait():
    time.sleep(5)

logging.basicConfig(filename='pidrator.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %I:%M:%S%p')
logging.info('Starting up pidrator engine.')
userwait()
logging.info('Shutting down pidrator engine.')
userquit()