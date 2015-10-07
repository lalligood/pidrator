#! python3
__author__ = 'lalligood'

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

major, minor, bugfix = platform.python_version_tuple()
if int(major) < 3: # Verify running python3
    print('pidrator is written to run on python version 3. Please update,')
    sys.exit(1)
elif raspi and getpass.getuser() != 'root': # RasPi should only run as root
    print('For proper functionality, pidrator should be run as root (sudo)!')
    sys.exit(1)

'''
**** FUNCTIONS ****
'''

# Following is necessary for handling UUIDs with PostgreSQL
psycopg2.extras.register_uuid()

def cleanexit(exitcode): # Close DB connection & exit gracefully
    cur.close()
    conn.close()
    if exitcode > 0: # Log as error when not closing normally
        logging.error('Shutting down application prematurely with exit status ' + str(exitcode) + '.')
    else:
        logging.info('Shutting down application with exit status ' + str(exitcode) + '.')
    sys.exit(exitcode)

def errmsgslow(text): # Print message & pause for 2 seconds
    print(text)
    time.sleep(2)

def dbinput(text, input_type): # Get user input & format for use in query
    response = ''
    if input_type == 'pswd':
        response = getpass.getpass(text)
        dbformat = eval('(\'' + response + '\', )')
    elif input_type == 'user':
        response = input(text)
        dbformat = eval('(\'' + response.lower() + '\', )')
    else:
        response = input(text)
        dbformat = eval('(\'' + response + '\', )')
    return dbformat

def dbnumber(number): # Get date value & format for inserting into database
    response = eval('(\'' + str(number) + '\', )')
    return response

def dbdate(date): # Get date value & format for inserting into database
    response = eval('(\'' + datetime.strftime(date, date_format) + '\', )')
    return response

def query(SQL, params, fetch, commit): # General purpose query submission that will exit if error
    try:
        cur.execute(SQL, params)
        logging.info('Query executed successfully.')
        # fetch parameter: all = return rows, one = return only 1 row, else 0
        if fetch == 'all':
            row = cur.fetchall()
            return row
        elif fetch == 'one':
            row = cur.fetchone()
            return row
        # commit parameter: True = commit, else not necessary to commit
        if commit:
            conn.commit()
    except psycopg2.Error as dberror:
        logging.error(dberror.diag.severity + ' - ' + dberror.diag.message_primary)

def create_devices():
    query('create table devices (\
    id uuid not null default uuid_generate_v4()\
    , devicename text not null unique\
    , createdate timestamp with time zone default now()\
    , constraint devices_pkey primary key (id)\
    );', None, '', True)

def create_foodcomments():
    query('create table foodcomments (\
    jobinfo_id uuid not null\
    , foodcomments text\
    , createtime timestamp with time zone default now()\
    );', None, '', True)

def create_foods():
    query('create table foods (\
    id uuid not null default uuid_generate_v4()\
    , foodname text not null unique\
    , createdate timestamp with time zone default now()\
    , constraint foods_pkey primary key (id)\
    );', None, '', True)

def create_job_data():
    query('create table job_data (\
    id serial\
    , job_id uuid\
    , moment timestamp with time zone\
    , temp_c double precision\
    , temp_f double precision\
    , constraint job_data_pkey primary key (id)\
    );', None, '', True)

def create_job_info():
    query('create table job_info (\
    id uuid not null default uuid_generate_v4()\
    , jobname text not null unique\
    , user_id uuid\
    , device_id uuid\
    , food_id uuid\
    , temperature_deg int\
    , temperature_setting text\
    , createtime timestamp with time zone default now()\
    , starttime timestamp with time zone\
    , endtime timestamp with time zone\
    , cookminutes int\
    , constraint job_info_pkey primary key (id)\
    );', None, '', True)

def create_users():
    query('create table users (\
    id uuid not null default uuid_generate_v4()\
    , username text not null unique\
    , fullname text not null\
    , email_address text not null unique\
    , "password" text not null\
    , createdate timestamp with time zone default now()\
    , constraint users_pkey primary key (id)\
    );', None, '', True)

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
logfilename = 'sql_test.log'
loglevel = logging.WARNING # Available logging levels, from low to high: DEBUG, INFO, WARNING, ERROR, CRITICAL
logformat = '%(time.asctime)s %(levelname)s: %(message)s'
logging.basicConfig(filename=logfilename, level=loglevel, format=logformat, datefmt=date_format)
logging.info('Initializing application & attempting to connect to database.')
# Hardware configuration
power_pin = 23 # GPIO pin 23

'''
**** MAIN ROUTINE ****
'''

# Open connection to database
try:
    conn = psycopg2.connect(database=dbname, user=dbuser, port=dbport)
    cur = conn.cursor()
    logging.info('Connected to database successfully')
except psycopg2.Error as dberror:
    logging.critical('Unable to connect to database. Is it running?')
    cleanexit(1)

# Check to see if all tables exists
schema = ('public', )
tables = query('select \
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
if len(results_list) > 0:
# If either of the following lines fail, then it should return error
# message & terminate that postgres-contrib-9.x and/or postgres-9.4-pgcrypto
# need to be installed.
    query('create extension if not exists "uuid-ossp";', None, '', False)
    query('create extension if not exists "pgcrypto";', None, '', False)
    for result in results_list:
        options = {
            'devices' : create_devices,
            'foodcomments' : create_foodcomments,
            'foods' : create_foods,
            'job_data' : create_job_data,
            'job_info' : create_job_info,
            'users' : create_users,
            }
        options[result]()
else:
    print('All tables present & accounted for. Skipping...')

cleanexit(0)
