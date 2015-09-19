#!/usr/bin/python3
__author__ = 'lalligood'

from datetime import datetime, timedelta
import getpass
import logging
import psycopg2
import psycopg2.extras
import sys
import time

# Following is necessary for handling UUIDs with PostgreSQL
psycopg2.extras.register_uuid()

def cleanexit(exitcode): # Close DB connection & exit gracefully
    cur.close()
    conn.close()
    if exitcode > 0: # Log as error when not closing normally
        logging.error('Shutting down application prematurely with exit status ' + str(exitcode) + '.')
    else:
        logging.info('Shutting down application with exit status ' + str(exitcode) + '.')
    sys.exit(exitcode)

def dbconnect(dbname, dbuser, dbport): # Connect to the database
    try:
        connection = psycopg2.connect(database=dbname, user=dbuser, port=dbport)
        cursor = connection.cursor()
        logging.info('Connected to database successfully')
        return cursor
    except psycopg2.Error as dberror:
        logging.critical('Unable to connect to database. Is it running?')
        cleanexit(1)

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

def dbnumber(number): # Get date value & format for inserting into database
    response = eval('(\'' + str(number) + '\', )')
    return response

def dbdate(date): # Get date value & format for inserting into database
    response = eval('(\'' + datetime.strftime(date, date_format) + '\', )')
    return response

def query(SQL, params, fetch, commit): # General purpose query submission that will exit if error
    try:
        cur.execute(SQL, params)
        logging.info('Query executed successfully.')
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
        logging.error(dberror.diag.severity + ' - ' + dberror.diag.message_primary)
        cleanexit(1)

def picklist(listname, colname, tablename, ordername):
    while True:
        print('The following ' + listname + ' are available: ')
        itemlist = query('select ' + colname + ' from ' + tablename + ' order by ' + ordername, '', 'all', False)
        count = 0
        for x in itemlist: # Display list
            count += 1
            print('    ' + str(count) + '. ' + x[0])
        print('    0. Add an item to the list.')
        countlist = count
        itemnbr = int(input('Enter the number of the item that you want to use: '))
        if itemnbr == 0: # Add new item to the table
            newitem = dbinput('Enter the name of the item you would like to add: ', '')
            confirm = input('You entered: ' + newitem[0] + '. Is that correct? [y/n]')
            if confirm.lower() == 'y': # Confirm this is what they want to add
                existingitem = query('select ' + colname + ' from ' + tablename + ' where ' + colname + ' = (%s)', newitem, 'one', False)
                if newitem == existingitem: # If existing item is found, disallow
                    print('That item already exists in the list. Please try again...')
                    time.sleep(2)
                    continue
                else: # Insert new item into table
                    query('insert into ' + tablename + ' (' + colname + ') values ((%s))', newitem, '', True)
                    print('Your new item has been added to the list.')
                    print('Returning to list of available ' + listname + '.')
            else:
                print('Invalid entry. Please try again...')
            time.sleep(2)
            continue
        elif itemnbr < 0 or itemnbr > countlist: # Verify input is valid
            print('Invalid selection. Please try again...')
            time.sleep(2)
            continue
        else: # Find the item in the list
            count = 0
            for x in itemlist: # Iterate & find selected value
                count += 1
                if count == itemnbr:
                    itemname = x
                    print('You selected: ' + itemname[0] + '.')
                    return itemname
                    break

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

'''
**** PARAMETERS ****
'''

# For inserting dates to DB & for logging
date_format = '%Y-%m-%d %H:%M:%S' # YYYY-MM-DD HH:MM:SS
# Logging information
logfilename = 'sql_test.log'
loglevel = logging.WARNING # Available logging levels, from low to high: DEBUG, INFO, WARNING, ERROR, CRITICAL
logformat = '%(time.asctime)s %(levelname)s: %(message)s'
logging.basicConfig(filename=logfilename, level=loglevel, format=logformat, datefmt=date_format)
logging.info('Initializing application & attempting to connect to database.')

'''
**** MAIN ROUTINE ****
'''

# Open connection to database
cur = dbconnect('postgres', 'lalligood', 5433)

'''
EVERYTHING BELOW THIS POINT IS THE MAIN ROUTINES FROM sql_test, sql_pswd_test, & timer_test

This all needs to be organized (& functionalized further if necessary) into a cohesive routine
'''
#**** BEGIN FROM sql_pswd_test.py ****
user = loginmenu()
while True:
    response = input('Do you want to change your password? [Y/N] ')
    if response.lower() == 'y':
        changepswd(user)
        break
    else:
        print('Invalid selection. Please try again...')
        time.sleep(2)
#**** END FROM sql_pswd_test.py ****

#**** BEGIN FROM sql_test.py ****
# Pick job from list
jobname = picklist('job names', 'jobname', 'job_info', 'createtime')
jobid = query('select id from job_info where jobname = (%s)', jobname, 'one', False)

# Pick user from list
username = picklist('users', 'username', 'users', 'username')
user = query('select id from users where username = (%s)', username, 'one', False)

# Pick cooking device from list
devname = picklist('cooking devices', 'devicename', 'devices', 'devicename')
device = query('select id from devices where devicename = (%s)', devname, 'one', False)

# Pick food from list
foodname = picklist('foods', 'foodname', 'foods', 'foodname')
food = query('select id from foods where foodname = (%s)', foodname, 'one', False)

# Update user_id, device_id, & food_id in job_info
query('update job_info set user_id = (%s), device_id = (%s), food_id = (%s) where jobname = (%s)', user + device + food + jobname, 'none', True)

# Now make sure it worked...!
row = query('select \
    jobname \
    , fullname \
    , devicename \
    , foodname \
from job_info \
    left outer join users on job_info.user_id = users.id \
    left outer join devices on job_info.device_id = devices.id \
    left outer join foods on job_info.food_id = foods.id \
where jobname = (%s)', jobname, 'one', False)
# Convert tuple to list
list(row)
print('Job:    ', row[0])
print('Name:   ', row[1])
print('Device: ', row[2])
print('Food:   ', row[3])
#**** END FROM sql_test.py ****

#**** BEGIN FROM timer_test.py ****
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
cooktime = dbnumber((cookhour * 60) + cookmin)
end = start + cookdelta
endtime = dbdate(end)
query('update job_info set endtime = (%s), cookminutes = (%s) where jobname = (%s)', endtime + cooktime + newjob, '', True)
print('Your job is going to cook for ' + str(cookhour) + ' hour(s) and ' + str(cookmin) + ' minute(s). It will complete at ' + endtime[0] + '.')

# Main cooking loop
currdelta = timedelta(seconds=30) # How often it should log data while cooking
temp = dbnumber(100) # This is a temporary placeholder value!
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
#**** END FROM timer_test.py ****
