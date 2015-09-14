#!/usr/bin/python3
__author__ = 'lalligood'

import psycopg2
import psycopg2.extras
import sys
import datetime
import time
import logging

psycopg2.extras.register_uuid()
date_format = '%Y-%m-%d %H:%M:%S' # YYYY-MM-DD HH:MM:SS

# Configure logging
logfilename = 'sql_test.log'
#loglevel = logging.DEBUG
#loglevel = logging.INFO
loglevel = logging.WARNING
#loglevel = logging.ERROR
#loglevel = logging.CRITICAL
logformat = '%(time.asctime)s %(levelname)s: %(message)s'
logging.basicConfig(filename=logfilename, level=loglevel, format=logformat, datefmt=date_format)

def cleanexit(exitcode): # Close DB connection & exit gracefully
    cur.close()
    conn.close()
    logging.info('Shutting down application with exit status ' + exitcode + '.')
    sys.exit(exitcode)

def dbinput(text, input_type): # Get user input & format for use in query
    response = ''
    if input_type = 'pswd':
        response = getpass.getpass(text)
        eval('(\'' + response + '\', )')
    elif input_type = 'user':
        response = input(text)
        eval('(\'' + response.lower() + '\', )')
    else:
        response = input(text)
        eval('(\'' + response + '\', )')
    return response

def query(SQL, params, fetch, commit): # General purpose query submission that will exit if error
    try:
        cur.execute(SQL, params)
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
        cleanexit(1)

################
# MAIN ROUTINE #
################

logging.info('Initializing application & attempting to connect to database.')
# DB connection info
mydb = 'postgres'
mydbuser = 'lalligood'
mydbport = 5433

# Connect to DB
try:
    conn = psycopg2.connect(database=mydb, user=mydbuser, port=mydbport)
    cur = conn.cursor()
    logging.info('Connected to database successfully')
except psycopg2.Error as dberror:
    logging.critical('Unable to connect to database. Is it running?')
    cleanexit(1)

# INSERT
'''
devname = ('stove', )
query('insert into devices (devicename) values (%s) returning *', devname, 'none', True)
'''

# SELECT w/o WHERE
'''
row = query('select username, fullname, email_address from users', '', 'one', False)
print('Your username is: ' + row[0])
print('Your name is: ' + row[1])
print('Your email address is: ' + row[2])
print('But I\'m not telling you what your password is!')
'''

# SELECT w/ WHERE
'''
params = ('slow cooker', )
row = query('select * from devices where devicename = (%s)', params, 'one', False)
print('slow cooker ID is: ' + row[0])
created = row[2].strftime('%m-%d-%Y %H:%M:%S')
print('slow cooker was added to DB on: ' + created)
'''

# SELECT w/ multiple parameters being passed in
# INSERT new job_info row first!
'''
params = ('third time is a charm', )
query('insert into job_info (jobname) values (%s) returning *', params, 'none', True)
'''

# Retrieve list of job names from job_info
print('Here is a list of job names: ')
joblist = query('select jobname from job_info order by createtime', '', 'all', False)
for x in joblist:
    print(x[0])

# Get user input & SELECT row from job_info based on input
# Format response appropriately as variable
jobname = dbinput('Enter the name of the job that you want to modify: ', '')
# Check to see if response matches result(s) here
'''
'''
# Fetch job ID for selected job
jobid = query('select id from job_info where jobname = (%s)', jobname, 'one', False)

# SELECT username from users
print('Here is a list of users: ')
userlist = query('select username from users order by username', '', 'all', False)
for x in userlist:
    print(x[0])
username = dbinput('Enter the username you want to add to the selected job: ', 'user')
user = query('select id from users where username = (%s)', username, 'one', False)

# SELECT devicename from devices
print('Here is a list of devices: ')
devlist = query('select devicename from devices order by devicename', '', 'all', False)
for x in devlist:
    print(x[0])
devname = dbinput('Enter the username you want to add to the selected job: ', '')
device = query('select id from devices where devicename = (%s)', devname, 'one', False)

# SELECT foodname from foods
print('Here is a list of foods: ')
foodlist = query('select foodname from foods order by foodname', '', 'all', False)
for x in foodlist:
    print(x[0])
foodname = dbinput('Enter the username you want to add to the selected job: ', '')
food = query('select id from foods where foodname = (%s)', foodname, 'one', False)

# UPDATE user_id & device_id in job_info
query('update job_info set user_id = (%s), device_id = (%s), food_id = (%s) where jobname = (%s)', user + device + food + jobname, 'none', True)

# Make sure it worked...!
row = query('select \
    jobname \
    , fullname \
    , devicename \
    , foodname \
from job_info \
    left outer join users on job_info.user_id = users.id \
    left outer join devices on job_info.device_id = devices.id \
    left outer join foods on job_info.food_id = foods.id \
where jobname = (%s)', jobname, 'one', False)
# Convert tuple to list
list(row)
print('Job: ', row[0])
print('Name: ', row[1])
print('Device: ', row[2])
print('Food: ', row[3])
cleanexit(0)
