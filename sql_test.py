#!/usr/bin/python3

import psycopg2
import sys
import datetime

# DB connection info
mydb = 'postgres'
mydbuser = 'lalligood'
mydbport = 5433

# Connect to DB
conn = psycopg2.connect(database=mydb, user=mydbuser, port=mydbport)
cur = conn.cursor()

# INSERT
#SQL = 'insert into devices (devicename) values (%s) returning *'
#devname = ('stove', )
#cur.execute(SQL, devname)
#conn.commit()

# SELECT w/o WHERE
SQL = 'select username, fullname, email_address from users;'
cur.execute(SQL)
row = cur.fetchone()
print('Your username is: ' + row[0])
print('Your name is: ' + row[1])
print('Your email address is: ' + row[2])
print('But I\'m not telling you what your password is!')

# SELECT w/ WHERE
SQL = 'select * from devices where devicename = (%s)'
devname = ('slow cooker', )
cur.execute(SQL, devname)
row = cur.fetchone()
print('slow cooker ID is: ' + row[0])
created = row[2].strftime('%m-%d-%Y %H:%M:%S')
print('slow cooker was added to DB on: ' + created)

# Close DB connection & exit gracefully
cur.close()
conn.close()
sys.exit()
