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

def query(): # General purpose query submission that will exit if error
    try:
        cur.execute(SQL, params)
    except psycopg2.Error as dberror:
        logging.error(dberror.diag.severity + ' - ' + dberror.diag.message_primary)
        cleanexit(1)

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
SQL = 'insert into devices (devicename) values (%s) returning *'
devname = ('stove', )
query()
conn.commit()
'''

# SELECT w/o WHERE
'''
SQL = 'select username, fullname, email_address from users'
params = ''
query()
row = cur.fetchone()
print('Your username is: ' + row[0])
print('Your name is: ' + row[1])
print('Your email address is: ' + row[2])
print('But I\'m not telling you what your password is!')
'''

# SELECT w/ WHERE
'''
SQL = 'select * from devices where devicename = (%s)'
params = ('slow cooker', )
query()
row = cur.fetchone()
print('slow cooker ID is: ' + row[0])
created = row[2].strftime('%m-%d-%Y %H:%M:%S')
print('slow cooker was added to DB on: ' + created)
'''

# SELECT w/ multiple parameters being passed in
# INSERT new job_info row first!
'''
SQL = 'insert into job_info (jobname) values (%s) returning *'
params = ('third time is a charm', )
query()
conn.commit()
'''

# Retrieve list of job names from job_info
print('Here is a list of job names: ')
SQL = 'select jobname from job_info order by createtime'
params = ''
query()
joblist = cur.fetchall()
for x in joblist:
    print(x)

# Get user input & SELECT row from job_info based on input
response = input('Enter the name of the job that you want to modify: ')
# Format response appropriately as variable
jobname = eval('(\'' + response + '\', )')
# Check to see if response matches result(s) here
'''
'''
# Fetch job ID for selected job
SQL = 'select id from job_info where jobname = (%s)'
params = jobname
query()
jobid = cur.fetchone()
logging.info('Retrieved ' + str(jobid) + ' from database successfully.')

# SELECT username from users
print('Here is a list of users: ')
SQL = 'select username from users order by username'
params = ''
query()
userlist = cur.fetchall()
for x in userlist:
    print(x)
response = input('Enter the username you want to add to the selected job: ')
username = eval('(\'' + response + '\', )')
SQL = 'select id from users where username = (%s)'
params = username
query()
user = cur.fetchone()
logging.info('Retrieved ' + str(username) + ' from database successfully.')

# SELECT devicename from devices
print('Here is a list of devices: ')
SQL = 'select devicename from devices order by devicename'
params = ''
query()
devlist = cur.fetchall()
for x in devlist:
    print(x)
response = input('Enter the username you want to add to the selected job: ')
devname = eval('(\'' + response + '\', )')
SQL = 'select id from devices where devicename = (%s)'
params = devname
query()
device = cur.fetchone()
logging.info('Retrieved ' + str(devname) + ' from database successfully.')

# SELECT foodname from foods
print('Here is a list of foods: ')
SQL = 'select foodname from foods order by foodname'
params = ''
query()
foodlist = cur.fetchall()
for x in foodlist:
    print(x)
response = input('Enter the username you want to add to the selected job: ')
foodname = eval('(\'' + response + '\', )')
SQL = 'select id from foods where foodname = (%s)'
params = foodname
query()
food = cur.fetchone()

# UPDATE user_id & device_id in job_info
SQL = 'update job_info set user_id = (%s), device_id = (%s), food_id = (%s) where jobname = (%s)'
params = user + device + food + jobname
query()
conn.commit()

# Make sure it worked...!
SQL = 'select \
    jobname \
    , fullname \
    , devicename \
    , foodname \
from job_info \
    left outer join users on job_info.user_id = users.id \
    left outer join devices on job_info.device_id = devices.id \
    left outer join foods on job_info.food_id = foods.id \
where jobname = (%s)'
params = jobname
query()
row = cur.fetchone()
# Convert tuple to list
list(row)
print('Job: ', row[0])
print('Name: ', row[1])
print('Device: ', row[2])
print('Food: ', row[3])
cleanexit(0)
