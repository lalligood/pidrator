#!/usr/bin/python3
__author__ = 'lalligood'

import psycopg2
import psycopg2.extras
import sys
import datetime
import time
import getpass

psycopg2.extras.register_uuid()

def cleanexit(ec): # Close DB connection & exit gracefully
    cur.close()
    conn.close()
    sys.exit(ec)

def query(SQL, params): # General purpose query submission that will exit if error
    try:
        cur.execute(SQL, params)
    except psycopg2.Error as dberror:
        print(dberror.diag.severity + ' - ' + dberror.diag.message_primary)
        cleanexit(1)

def userlogin(user): # User login
    response = getpass.getpass('Enter your password: ')
    pswd = eval('(\'' + response + '\', )')
    SQL = 'select (password = crypt((%s), password)) as userpass from users where username = (%s)'
    params = pswd + user
    query(SQL, params)
    pswdverify = cur.fetchone()
    if pswdverify[0]:
        print('Password entered successfully!')
    else:
        print('Username and/or password incorrect. Try again...')
        time.sleep(2)
        userlogin(user)

def changepswd(user): # User elects to change password
    while True:
        response = getpass.getpass('Enter your current password: ')
        oldpswd = eval('(\'' + response + '\', )')
        response = getpass.getpass('Enter your new password: ')
        newpswd1 = eval('(\'' + response + '\', )')
        response = getpass.getpass('Enter your new password again: ')
        newpswd2 = eval('(\'' + response + '\', )')
        if newpswd1[0] != newpswd2[0]:
            print('New passwords do not match. Try again...')
            time.sleep(2)
            continue
        if len(newpswd1[0]) < 8:
            print('New password length is too short. Try again...')
            time.sleep(2)
            continue
        if oldpswd[0] == newpswd1[0]:
            print('New password must be different from old password. Try again...')
            time.sleep(2)
            continue
        SQL = 'select (password = crypt((%s), password)) as userpass from users where username = (%s)'
        params = oldpswd + user
        query(SQL, params)
        pswdverify = cur.fetchone()
        if pswdverify[0]:
            SQL = 'update users set password = crypt((%s), gen_salt(\'bf\')) where username = (%s)'
            params = newpswd1 + user
            query(SQL, params)
            conn.commit()
            print('Your password has been updated successfully.')
            break
        else:
            print('Old password incorrect. Try again...')
            time.sleep(2)

# DB connection info
mydb = 'postgres'
mydbuser = 'lalligood'
mydbport = 5433

# Connect to DB
conn = psycopg2.connect(database=mydb, user=mydbuser, port=mydbport)
cur = conn.cursor()

response = input('Enter your username: ')
user = eval('(\'' + response.lower() + '\', )')
userlogin(user)
changepswd(user)
cleanexit(0)
