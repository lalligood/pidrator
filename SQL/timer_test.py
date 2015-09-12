#!/usr/bin/python3
__author__ = 'lalligood'

import psycopg2
import psycopg2.extras
import sys
from datetime import datetime, timedelta

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
SQL = 'select jobname from job_info order by createtime'
params = ''
query()
jobs = cur.fetchall()
for jobname in jobs:
    print('    ' + jobname[0])
response = input('Enter the job name that you want to run: ')
currjob = eval('(\'' + response + '\', )')

# Insert start time into job_info row
start = datetime.now()
starttime = eval('(\'' + datetime.strftime(start, date_format) + '\', )')
SQL = 'update job_info set starttime = (%s) where jobname = (%s) returning *'
params = starttime + currjob 
query()
conn.commit()
row = cur.fetchone()

# Get user input to determine how long job should be
cookhour = int(input('Enter the number of hours that you want to cook: '))
cookmin = int(input('Enter the number of minutes that you want to cook: '))
cookdelta = timedelta(hours=cookhour, minutes=cookmin)
end = start + cookdelta
endtime = eval('(\'' + datetime.strftime(end, date_format) + '\', )')
SQL = 'update job_info set endtime = (%s) where jobname = (%s) returning *'
params = endtime + currjob 
query()
conn.commit()
row = cur.fetchone()
print('Your job is going to cook for ' + str(cookhour) + ' hour(s) and ' + str(cookmin) + ' minute(s). It will complete at ' + endtime[0] + '.')

cleanexit()
