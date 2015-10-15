#! python3
__author__ = 'lalligood'

import core as c
import core.CreatePiTables as cpt
from datetime import datetime, timedelta
import getpass
import glob
import logging
import os
import platform
raspi = False
if platform.machine() == 'armv6l': # Enable some functionality ONLY if raspi!
    raspi = True
import psycopg2
import psycopg2.extras
if raspi:
    from RPi import GPIO
import sys
import time

# Following is necessary for handling UUIDs with PostgreSQL
psycopg2.extras.register_uuid()

'''
**** PARAMETERS ****
'''

# Database connection information
# There are 2 sets of DB connection variables below. ONLY USE ONE AT A TIME!
if raspi: # RASPI DB
    dbname = 'pi'
    dbuser = 'pi'
    dbport = 5432
else: # NON-RASPI TEST DB
    dbname = 'postgres'
    dbuser = 'lalligood'
    dbport = 5433
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

# Verify running python 3.x
(major, minor, patchlevel) = platform.python_version_tuple()
if int(major) < 3: # Verify running python3
    logging.error('pidrator is written to run on python version 3.')
    logging.error("Please update by running 'sudo apt-get install python3'.")
    sys.exit(1)
elif raspi and getpass.getuser() != 'root': # RasPi should only run as root
    logging.error('For proper functionality, pidrator should be run as root (sudo)!')
    sys.exit(1)

# Open connection to database
try:
    conn = psycopg2.connect(database=dbname, user=dbuser, port=dbport)
    cur = conn.cursor()
    logging.info('Connected to database successfully')
except psycopg2.Error as dberror:
    logging.critical('UNABLE TO CONNECT TO DATABASE. Is it running?')
    c.cleanexit(1)

# Check to see if all tables exists
schema = ('public', )
tables = c.query('select \
    table_name \
    from information_schema.tables \
    where table_schema = (%s) \
    order by table_name', schema, 'all', False)
tables_list = [] # Convert results tuple -> list
for table in tables:
    tables_list.append(table[0])
master_list = ['devices', 'foodcomments', 'foods', 'job_data', 'job_info', 'users']
# Get difference of master_list & tables_list
results_list = set(master_list).difference(tables_list)
# Create any tables that do not exist
if len(results_list) > 0:
    try:
        c.query('create extension if not exists "uuid-ossp";', None, '', False)
        c.query('create extension if not exists "pgcrypto";', None, '', False)
    except psycopg2.Error as dberror:
        logging.critical("Unable to create PostgreSQL extensions. Run 'apt-get install postgresql-contrib-9.4'.")
        c.cleanexit(1)
    for result in results_list:
        options = {
            'devices' : cpt.create_devices,
            'foodcomments' : cpt.create_foodcomments,
            'foods' : cpt.create_foods,
            'job_data' : cpt.create_job_data,
            'job_info' : cpt.create_job_info,
            'users' : cpt.create_users,
            }
        options[result]()
else:
    print('Confirmed that all tables present & accounted for. Exiting...')

c.cleanexit(0)
