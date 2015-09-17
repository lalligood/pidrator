#!/usr/bin/python3
__author__ = 'lalligood'

import psycopg2
import psycopg2.extras
import sys
from datetime import datetime, timedelta

psycopg2.extras.register_uuid()

def cleanexit(exitcode): # Close DB connection & exit gracefully
    cur.close()
    conn.close()
    sys.exit(exitcode)

def dbinput(text, input_type): # Get user input & format for use in query
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

def dbdate(date): # Get date value & format for inserting into database
    response = eval('(\'' + datetime.strftime(date, date_format) + '\', )')
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
        print(dberror.diag.severity + ' - ' + dberror.diag.message_primary)
        cleanexit(1)

date_format = '%Y-%m-%d %H:%M:%S'
# DB connection info
mydb = 'postgres'
mydbuser = 'lalligood'
mydbport = 5433

# Connect to DB
conn = psycopg2.connect(database=mydb, user=mydbuser, port=mydbport)
cur = conn.cursor()

# Retrieve list of job names from job_info
'''
print('Here is a list of job names: ')
jobs = query('select jobname from job_info order by createtime', '', 'all', False)
for jobname in jobs:
    print('    ' + jobname[0])
currjob = dbinput('Enter the job name that you want to run: ', '')
'''

# Enter the name of a new job
newjob = dbinput('What would you like to call your new job? ', '')
jobid = query('insert into job_info (jobname) values (%s) returning id', newjob, 'one', True)

# Insert start time into job_info row
start = datetime.now()
starttime = dbdate(start)
query('update job_info set starttime = (%s) where jobname = (%s)', starttime + newjob, '', True)

# Get user input to determine how long job should be
cookhour = int(input('Enter the number of hours that you want to cook: '))
cookmin = int(input('Enter the number of minutes that you want to cook: '))
cookdelta = timedelta(hours=cookhour, minutes=cookmin)
cooktime = eval('(\'' + str((cookhour * 60) + cookmin) + '\', )')
end = start + cookdelta
endtime = dbdate(end)
query('update job_info set endtime = (%s), cookminutes = (%s) where jobname = (%s)', endtime + cooktime + newjob, '', True)
print('Your job is going to cook for ' + str(cookhour) + ' hour(s) and ' + str(cookmin) + ' minute(s). It will complete at ' + endtime[0] + '.')

# Main cooking loop
currdelta = timedelta(seconds=30) # How often it should log data while cooking
temp = eval('(\'' + str(100) + '\', )') # This is a temporary placeholder value!
countdown = 0
while True:
    currtime = datetime.now()
    if currtime >= start + currdelta:
        current = dbdate(currtime)
        query('insert into job_data (job_id, moment, temperature) \
            values ((%s), (%s), (%s))',
            jobid + current + temp, '', True)
        start = datetime.now()
        countdown += 0.5
        print('You job has been active for ' + str(countdown) + ' minutes.')
    if currtime >= end:
        break

print('Job complete!')

cleanexit(0)
