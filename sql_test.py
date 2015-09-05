#!/usr/bin/python3

import psycopg2
import sys

# DB connection info
mydb = 'postgres'
mydbuser = 'lalligood'
mydbport = 5433

# Connect to DB
conn = psycopg2.connect(database=mydb, user=mydbuser, port=mydbport)
cur = conn.cursor()

#SQL = 'insert into devices (devicename) values (%s) returning *'
#devname = ('stove', )
#cur.execute(SQL, devname)
#conn.commit()
SQL = 'select username, fullname, email_address from users;'
cur.execute(SQL)
row = cur.fetchone()
print('Your username is: ' + row[0])
print('Your name is: ' + row[1])
print('Your email address is: ' + row[2])
print('But I\'m not telling you what your password is!')

# Close DB connection & exit gracefully
cur.close()
conn.close()
sys.exit()
