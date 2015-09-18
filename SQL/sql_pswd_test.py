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

def loginmenu(): # Welcome screen to login, create acct, or exit
    while True:
        menuopt = input('''pidrator Menu

Select from one of the following choices:
1) Login (must have an account)
2) Create a new account
x) Exit
''')
        if menuopt == '1':
            user = userlogin()
            return user
            break
        elif menuopt == '2':
            user = usercreate()
            return user
            break
        elif menuopt == 'x':
            print('Exiting pidrator...')
            cleanexit(0)
        else:
            print('Invalid choice. Please try again...')
            time.sleep(2)

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

def userlogin(): # User login
    while True:
        username = dbinput('Enter your username: ', 'user')
        pswd = dbinput('Enter your password: ', 'pswd')
        userverify = query('select username from users where username = (%s)', username, 'one', False)
        pswdverify = query('select (password = crypt((%s), password)) as userpass from users where username = (%s)', pswd + username, 'one', False)
        if userverify == None:
            print('Username and/or password incorrect. Try again...')
        elif pswdverify[0]:
            print('Password entered successfully!')
            return username
            break
        else:
            print('Username and/or password incorrect. Try again...')
        time.sleep(2) # Slow down any brute force login attempts

def usercreate(): # User login
    while True:
        username = dbinput('Enter your desired username: ', 'user')
        fullname = dbinput('Enter your full name: ', 'user')
        emailaddr = dbinput('Enter your email address: ', 'user')
        pswd = dbinput('Enter your password: ', 'pswd')
        pswdconfirm = dbinput('Enter your password: ', 'pswd')
        if pswd != pswdconfirm: # Make sure passwords match
            print('Your passwords do not match. Please try again...')
            time.sleep(2) # Slow down any brute force login attempts
            continue
        if len(pswd[0]) < 8: # Make sure passwords are long enough
            print('Your password is not long enough. Must be at least 8 characters. Try again...')
            time.sleep(2) # Slow down any brute force login attempts
            continue
        existinguser = query('select username from users where username = (%s)', username, 'one', False)
        if username == existinguser: # Make sure user doesn't already exist
            print('That username is already in use. Please try again...')
            time.sleep(2) # Slow down any brute force login attempts
            continue
        else:
            query('insert into users (username, fullname, email_address, password) values ((%s), (%s), (%s), crypt((%s), gen_salt(\'bf\')))', username + fullname + emailaddr + pswd, '', True)
            print('Your username was created successfully.')
            return username

def changepswd(username): # User elects to change password
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

user = loginmenu()
while True:
    response = input('Do you want to change your password? [Y/N] ')
    if response.lower() == 'y':
        changepswd(user)
        break
    else:
        print('Invalid selection. Please try again...')
        time.sleep(2)
cleanexit(0)
