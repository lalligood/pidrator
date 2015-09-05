#!/usr/bin/python3

import psycopg2
import sys

# Connect to DB
conn = psycopg2.connect('dbname=postgres user=lalligood port=5433')
cur = conn.cursor()

cur.execute('select * from users')
print(cur.fetchall())
input()

SQL = 'insert into devices (devicename) values (%s) returning *'
devname = ('stove', )
cur.execute(SQL, devname)
conn.commit()
print(cur.fetchall())
cur.close()
conn.close()
sys.exit()
