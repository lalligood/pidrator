#!/usr/bin/python3
__author__ = 'lalligood'

import psycopg2
import psycopg2.extras
import sys
import datetime
import time
import getpass

psycopg2.extras.register_uuid()

def cleanexit(exitcode): # Close DB connection & exit gracefully
    cur.close()
    conn.close()
    sys.exit(exitcode)

def dbinput(text, input_type): # Get user input & format for use in query
    response = ''
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

def userlogin(username): # User login
    pswd = dbinput('Enter your password: ', 'pswd')
    pswdverify = query('select (password = crypt((%s), password)) as userpass from users where username = (%s)', pswd + username, 'one', False)
    if pswdverify[0]:
        print('Password entered successfully!')
    else:
        print('Username and/or password incorrect. Try again...')
        time.sleep(2)
        userlogin(username)

def changepswd(user): # User elects to change password
    while True:
        oldpswd = dbinput('Enter your current password: ', 'pswd')
        newpswd1 = dbinput('Enter your new password: ', 'pswd')
        newpswd2 = dbinput('Enter your new password again: ', 'pswd')
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
        pswdverify = query('select (password = crypt((%s), password)) as userpass from users where username = (%s)', oldpswd + user, 'one', False)
        if pswdverify[0]:
            query('update users set password = crypt((%s), gen_salt(\'bf\')) where username = (%s)', newpswd1 + user, 'none', True)
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

user = dbinput('Enter your username: ', 'user')
userlogin(user)
changepswd(user)
cleanexit(0)
