#!/usr/bin/python3
__author__ = 'lalligood'

import psycopg2
import psycopg2.extras
import sys
import datetime

psycopg2.extras.register_uuid()

def cleanexit(exitcode): # Close DB connection & exit gracefully
    cur.close()
    conn.close()
    sys.exit(exitcode)

def query(SQL, params): # General purpose query submission that will exit if error
    try:
        cur.execute(SQL, params)
    except psycopg2.Error as dberror:
        print(dberror.diag.severity + ' - ' + dberror.diag.message_primary)
        cleanexit(1)

# DB connection info
mydb = 'postgres'
mydbuser = 'lalligood'
mydbport = 5433

# Connect to DB
conn = psycopg2.connect(database=mydb, user=mydbuser, port=mydbport)
cur = conn.cursor()

# INSERT
'''
devname = ('stove', )
query('insert into devices (devicename) values (%s) returning *', devname)
conn.commit()
'''

# SELECT w/o WHERE
'''
query('select username, fullname, email_address from users', '')
row = cur.fetchone()
print('Your username is: ' + row[0])
print('Your name is: ' + row[1])
print('Your email address is: ' + row[2])
print('But I\'m not telling you what your password is!')
'''

# SELECT w/ WHERE
'''
params = ('slow cooker', )
query('select * from devices where devicename = (%s)', params)
row = cur.fetchone()
print('slow cooker ID is: ' + row[0])
created = row[2].strftime('%m-%d-%Y %H:%M:%S')
print('slow cooker was added to DB on: ' + created)
'''

# SELECT w/ multiple parameters being passed in
# INSERT new job_info row first!
'''
params = ('third time is a charm', )
query('insert into job_info (jobname) values (%s) returning *', params)
conn.commit()
'''

# Retrieve list of job names from job_info
print('Here is a list of job names: ')
query('select jobname from job_info order by createtime', '')
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
query('select id from job_info where jobname = (%s)', jobname)
jobid = cur.fetchone()

# SELECT username from users
print('Here is a list of users: ')
query('select username from users order by username', '')
userlist = cur.fetchall()
for x in userlist:
    print(x)
response = input('Enter the username you want to add to the selected job: ')
username = eval('(\'' + response + '\', )')
query('select id from users where username = (%s)', username)
user = cur.fetchone()

# SELECT devicename from devices
print('Here is a list of devices: ')
query('select devicename from devices order by devicename', '')
devlist = cur.fetchall()
for x in devlist:
    print(x)
response = input('Enter the username you want to add to the selected job: ')
devname = eval('(\'' + response + '\', )')
query('select id from devices where devicename = (%s)', devname)
device = cur.fetchone()

# SELECT foodname from foods
print('Here is a list of foods: ')
query('select foodname from foods order by foodname', '')
foodlist = cur.fetchall()
for x in foodlist:
    print(x)
response = input('Enter the username you want to add to the selected job: ')
foodname = eval('(\'' + response + '\', )')
query('select id from foods where foodname = (%s)', foodname)
food = cur.fetchone()

# UPDATE user_id & device_id in job_info
query('update job_info set user_id = (%s), device_id = (%s), food_id = (%s) where jobname = (%s)', user + device + food + jobname)
conn.commit()

# Make sure it worked...!
query('select \
    jobname \
    , fullname \
    , devicename \
    , foodname \
from job_info \
    left outer join users on job_info.user_id = users.id \
    left outer join devices on job_info.device_id = devices.id \
    left outer join foods on job_info.food_id = foods.id \
where jobname = (%s)', jobname)
row = cur.fetchone()
# Convert tuple to list
list(row)
print('Job: ', row[0])
print('Name: ', row[1])
print('Device: ', row[2])
print('Food: ', row[3])
cleanexit(0)
