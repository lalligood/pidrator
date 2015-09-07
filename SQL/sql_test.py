#!/usr/bin/python3

import psycopg2
import psycopg2.extras
import sys
import datetime

psycopg2.extras.register_uuid()

def cleanexit(): # Close DB connection & exit gracefully
    cur.close()
    conn.close()
    sys.exit()

def query(): # General purpose query submission that will exit if error
    try:
        cur.execute(SQL, params)
    except psycopg2.Error as dberror:
        print(dberror.diag.severity + ' - ' + dberror.diag.message_primary)
        cleanexit()

# DB connection info
mydb = 'postgres'
mydbuser = 'lalligood'
mydbport = 5433

# Connect to DB
conn = psycopg2.connect(database=mydb, user=mydbuser, port=mydbport)
cur = conn.cursor()

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

# SELECT W/ JOIN
# INSERT new job_info row first!
'''
SQL = 'insert into job_info (jobname) values (%s) returning *'
params = ('first time', )
query()
conn.commit()
'''

# Retrieve list of job names from job_info
print('Here is a list of job names: ')
SQL = 'select jobname from job_info'
params = ''
query()
jobname = cur.fetchall()
for x in jobname:
    print(x)

# Get user input & SELECT row from job_info based on input
print('Enter the name of the job that you want to modify: ')
response = input()
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

# SELECT username from users
SQL = 'select id from users where username = (%s)'
params = ('lalligood', )
query()
user = cur.fetchone()

# SELECT devicename from devices
SQL = 'select id from devices where devicename = (%s)'
params = ('slow cooker', )
query()
device = cur.fetchone()

# UPDATE user_id & device_id in job_info
SQL = 'update job_info set user_id = (%s), device_id = (%s) where jobname = (%s)'
params = user + device + jobname
query()
conn.commit()

# Make sure it worked...!
SQL = 'select * from job_info'
params = ''
query()
row = cur.fetchone()
print(row)
print('Row inserted & updated in job_info successfully!')
cleanexit()
