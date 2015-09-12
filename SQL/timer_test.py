#!/usr/bin/python3
__author__ = 'lalligood'

import psycopg2
import psycopg2.extras
import sys
import datetime
import time

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

# Retrieve list of job names from job_info
print('Here is a list of job names: ')
SQL = 'select jobname from job_info order by createtime'
params = ''
query()
jobs = cur.fetchall()
for jobname in jobs:
    print('    ' + jobname[0])

# Insert start time into job_info row
starttime = eval('(\'' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + '\', )')
SQL = "update job_info set starttime = (%s) where jobname = 'first time' returning *"
params = starttime
query()
conn.commit()
row = cur.fetchone()
print(row)
cleanexit()
