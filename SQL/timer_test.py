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
print('Here is a list of job names: ')
jobs = query('select jobname from job_info order by createtime', '', 'all', False)
for jobname in jobs:
    print('    ' + jobname[0])
currjob = dbinput('Enter the job name that you want to run: ', '')

# Insert start time into job_info row
start = datetime.now()
starttime = dbdate(start)
query('update job_info set starttime = (%s) where jobname = (%s)', starttime + currjob, 'none', True)

# Get user input to determine how long job should be
cookhour = int(input('Enter the number of hours that you want to cook: '))
cookmin = int(input('Enter the number of minutes that you want to cook: '))
cookdelta = timedelta(hours=cookhour, minutes=cookmin)
end = start + cookdelta
endtime = dbdate(end)
query('update job_info set endtime = (%s) where jobname = (%s)', endtime + currjob, 'none', True)
print('Your job is going to cook for ' + str(cookhour) + ' hour(s) and ' + str(cookmin) + ' minute(s). It will complete at ' + endtime[0] + '.')

cleanexit(0)
