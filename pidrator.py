#!/usr/bin/python3
__author__ = 'lalligood'

from datetime import datetime, timedelta
import getpass
import glob
import logging
import os
import platform
raspi = False
if platform.machine() == 'armv6l': # Enable some functionality ONLY if raspi!
    raspi = True
import psycopg2
import psycopg2.extras
if raspi:
    from RPi import GPIO
import sys
import time

'''
**** FUNCTIONS ****
'''

# Following is necessary for handling UUIDs with PostgreSQL
psycopg2.extras.register_uuid()

def cleanexit(exitcode):
    'Closes database connection & attempts to exit gracefully'
    cur.close()
    conn.close()
    if exitcode == 0: # Log as info when closing normally
        logging.info('Shutting down application with exit status ' + str(exitcode) + '.')
    else: # Log as error when closing abnormally
        logging.error('Shutting down application prematurely with exit status ' + str(exitcode) + '.')
    logging.shutdown()
    sys.exit(exitcode)

def errmsgslow(text): 
    'Prints message then pauses for 2 seconds'
    print(text)
    time.sleep(2)

def dbinput(text, input_type): 
    'Gets user input & formats input text for use in query as a parameter'
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

def dbnumber(number):
    'Gets numeric value & formats for use in query as a parameter'
    response = eval('(\'' + str(number) + '\', )')
    return response

def dbdate(date):
    'Gets date value & formats for use in query as a parameter'
    response = eval('(\'' + datetime.strftime(date, date_format) + '\', )')
    return response

def query(SQL, params, fetch, commit):
    '''General purpose query submission. Can be used for SELECT, UPDATE, INSERT, 
or DELETE queries, with or without parameters.'''
    try:
        cur.execute(SQL, params)
        logging.info("Query '" + SQL + "' executed successfully.")
        # fetch parameter: all = return many rows, one = return only 1 row, or 0
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
        logging.error('Failed query: ' + SQL)

def picklist(listname, colname, tablename, ordername):
    '''Displays a list of items referred as listname from the column name (colname)
from table (tablename) & the list is ordered by ordername is desired.
It then asks if you want to add item(s) to the list, select an item from the
list, or return an error if the choice is not valid.'''
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
            confirm = input('You entered: ' + newitem[0] + '. Is that correct? [Y/N] ')
            if confirm.lower() == 'y': # Confirm this is what they want to add
                existingitem = query('select ' + colname + ' from ' + tablename + ' where ' + colname + ' = (%s)', newitem, 'one', False)
                if newitem == existingitem: # If existing item is found, disallow
                    errmsgslow('That item already exists in the list. Please try again...')
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
            errmsgslow('Invalid selection. Please try again...')
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

def loginmenu():
    'Basic Welcome screen to login, create acct, or exit'
    while True:
        menuopt = input('''
pidrator Menu

Select from one of the following choices:
    1. Login (must have an account)
    2. Create a new account
    x. Exit
Enter your selection: ''')
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
            errmsgslow('Invalid choice. Please try again...')

def userlogin():
    'Handles user login by verifying that the user & password are correct.'
    badlogin = 0 # Counter for login attempts; 3 strikes & you're out
    while True:
        username = dbinput('Enter your username: ', 'user')
        pswd = dbinput('Enter your password: ', 'pswd')
        userverify = query('select username from users where username = (%s)', username, 'one', False)
        pswdverify = query('select (password = crypt((%s), password)) as userpass from users where username = (%s)', pswd + username, 'one', False)
        if userverify == None: # User not found
            badlogin += 1
        elif pswdverify[0]: # Allow if username & password successful
            print('Login successful.')
            return username
            break
        else: # Password does not match
            badlogin += 1
        if badlogin == 3: # Quit after 3 failed logins
            print('Too many incorrect login attempts.')
            cleanexit(1)
        else: # Failed login message & try again
            errmsgslow('Username and/or password incorrect. Try again...')

def usercreate():
    'Create a new user.'
    while True:
        username = dbinput('Enter your desired username: ', 'user')
        fullname = dbinput('Enter your full name: ', '')
        emailaddr = dbinput('Enter your email address: ', '')
        pswd = dbinput('Enter your password: ', 'pswd')
        pswdconfirm = dbinput('Enter your password: ', 'pswd')
        if pswd != pswdconfirm: # Make sure passwords match
            errmsgslow('Your passwords do not match. Please try again...')
            continue
        if len(pswd[0]) < 8: # Make sure passwords are long enough
            errmsgslow('Your password is not long enough. Must be at least 8 characters. Try again...')
            continue
        existinguser = query('select username from users where username = (%s)', username, 'one', False)
        if username == existinguser: # Make sure user doesn't already exist
            errmsgslow('That username is already in use. Please try again...')
            continue
        else: # If all conditions met, then add user
            query('insert into users (username, fullname, email_address, password) values ((%s), (%s), (%s), crypt((%s), gen_salt(\'bf\')))', username + fullname + emailaddr + pswd, '', True)
            print('Your username was created successfully.')
            return username

def changepswd(username):
    'Allows the user to change their password.'
    while True:
        oldpswd = dbinput('Enter your current password: ', 'pswd')
        newpswd1 = dbinput('Enter your new password: ', 'pswd')
        newpswd2 = dbinput('Enter your new password again: ', 'pswd')
        if newpswd1[0] != newpswd2[0]:
            errmsgslow('New passwords do not match. Try again...')
            continue
        if len(newpswd1[0]) < 8:
            errmsgslow('New password length is too short. Try again...')
            continue
        if oldpswd[0] == newpswd1[0]:
            errmsgslow('New password must be different from old password. Try again...')
            continue
        pswdverify = query('select (password = crypt((%s), password)) as userpass from users where username = (%s)', oldpswd + user, 'one', False)
        if pswdverify[0]:
            query('update users set password = crypt((%s), gen_salt(\'bf\')) where username = (%s)', newpswd1 + user, 'none', True)
            print('Your password has been updated successfully.')
            break
        else:
            errmsgslow('Old password incorrect. Try again...')

def powertail(onoff):
    'If device if present, it turns Powertail on/off.'
    if raspi:
        if onoff:
            GPIO.output(power_pin, True) # Powertail on
        else:
            GPIO.output(power_pin, False) # Powertail off

def readtemp():
    'If device is present, it will open a connection to thermal sensor.'
    if raspi:
        sensor = open(sensor_file, 'r') # Open thermal sensor "file"
        rawdata = sensor.readlines() # Read sensor
        sensor.close() # Close "file"
        return rawdata

def gettemp():
    'Reads thermal sensor until it gets a valid result.'
    if raspi:
        results = readtemp()                    # Read sensor
        while results[0].strip()[-3:] != 'YES': # Continue to read until result
            results = readtemp()                # is valid, just in case
        validate = results[1].find('t=')
        if validate != -1:
            parse_temp = lines[1][equals_pos + 2:]
            temp_c = round((float(parse_temp) / 1000.0), 3)
            temp_f = round((temp_c * 9.0 / 5.0 + 32.0), 3)
            return temp_c, temp_f # Return temp to 3 decimal places in C & F

'''
**** PARAMETERS ****
'''

# Database connection information
# There are 2 sets of DB connection variables below. ONLY USE ONE AT A TIME!
if raspi: # RASPI DB
    dbname = 'pi'
    dbuser = 'pi'
    dbport = 5432
else: # NON-RASPI TEST DB
    dbname = 'postgres'
    dbuser = 'lalligood'
    dbport = 5433
# For inserting dates to DB & for logging
date_format = '%Y-%m-%d %H:%M:%S' # YYYY-MM-DD HH:MM:SS
# Logging information
logfilename = 'pidrator.log'
loglevel = logging.DEBUG # Available logging levels, from low to high: DEBUG, INFO, WARNING, ERROR, CRITICAL
logformat = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(filename=logfilename, level=loglevel, format=logformat, datefmt=date_format)
logging.info('Initializing application & attempting to connect to database.')
# Hardware configuration
power_pin = 23 # GPIO pin 23

'''
**** MAIN ROUTINE ****
'''

# Verify running python 3.x
(major, minor, patchlevel) = platform.python_version_tuple()
if int(major) < 3: # Verify running python3
    logging.error('pidrator is written to run on python version 3.')
    logging.error("Please update by running 'sudo apt-get install python3'.")
    sys.exit(1)
elif raspi and getpass.getuser() != 'root': # RasPi should only run as root
    logging.error('For proper functionality, pidrator should be run as root (sudo)!')
    sys.exit(1)

# Enable all devices attached to RaspPi GPIO
if raspi:
    # Powertail configuration
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(power_pin, GPIO.OUT)
        GPIO.output(power_pin, False) # Make sure powertail is off!
    except:
        logging.error('Powertail not found or connected. Cannot cook anything without it!')
        sysexit(1)
    # Thermal sensor configuration
    try:
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')
        base_dir = '/sys/bus/w1/devices/'               # Navigate path to
        device_folder = glob.glob(base_dir + '28*')[0]  # thermal sensor
        sensor_file = device_folder + '/w1_slave'       # "file"
        therm_sens = True
    except:
        logging.warning('Thermal sensor not found or connected.')
        logging.warning('Unable to record temperature while cooking.')
        therm_sens = False

# Open connection to database
try:
    conn = psycopg2.connect(database=dbname, user=dbuser, port=dbport)
    cur = conn.cursor()
    logging.info('Connected to database successfully')
except psycopg2.Error as dberror:
    logging.critical('Unable to connect to database. Is it running?')
    cleanexit(1)

# User login
user = loginmenu()
print('\n\n')

# User password change (optional)
while True:
    response = input('Do you want to change your password? [Y/N] ')
    if response.lower() == 'y':
        changepswd(user)
        break
    elif response.lower() == 'n':
        break
    else:
        print('Invalid selection. Please try again...')
        time.sleep(2)
print('\n\n')

# Pick job from list
jobname = picklist('job names', 'jobname', 'job_info', 'createtime')
jobid = query('select id from job_info where jobname = (%s)', jobname, 'one', False)
print('\n\n')

# Pick cooking device from list
devname = picklist('cooking devices', 'devicename', 'devices', 'devicename')
deviceid = query('select id from devices where devicename = (%s)', devname, 'one', False)
print('\n\n')

# Pick food from list
foodname = picklist('foods', 'foodname', 'foods', 'foodname')
foodid = query('select id from foods where foodname = (%s)', foodname, 'one', False)
print('\n\n')

# Get user_id
userid = query('select id from users where username = (%s)', user, 'one', False)

# Get temperature setting
tempcheck = query('select temperature from job_info where id = (%s)', jobid, 'one', False)
if tempcheck[0] == None: # No previous cooking data available
    print('No previous temperature found.')
    tempset = dbinput('What temperature (degrees or setting) are you going to cook your job at? ', '')
else: # Previous cooking data available
    while True: # Will food will be cooked at same temp as last time?
        print('Last job was cooked at temperature/setting: ' + tempcheck[0] + '.')
        response = input('Are you going to cook at the same temperature/setting? [Y/N] ')
        if response.lower() == 'y': # Cook at the same temp
            print('You selected to cook at the same temperature/setting.')
            tempset = tempcheck
            break
        elif response.lower() == 'n': # Cook at a different temp
            tempset = dbinput('What temperature/setting are you going to use this time? ', '')
            break
        else:
            errmsgslow('Invalid selection. Please try again...')
print('\n\n')

# Update user_id, device_id, & food_id in job_info
query('update job_info set user_id = (%s), device_id = (%s),\
    food_id = (%s), temperature = (%s) where id = (%s)',
    userid + deviceid + foodid + tempset + jobid, 'none', True)

# Now make sure it worked...!
row = query('select \
    jobname \
    , users.fullname \
    , devices.devicename \
    , foods.foodname \
    , temperature \
from job_info \
    left outer join users on job_info.user_id = users.id \
    left outer join devices on job_info.device_id = devices.id \
    left outer join foods on job_info.food_id = foods.id \
where jobname = (%s)', jobname, 'one', False)
# Convert tuple to list
list(row)
print('\n\n')
print('    Job name:            ', row[0])
print('    Prepared by:         ', row[1])
print('    Cooking device:      ', row[2])
print('    Food being prepared: ', row[3])
print('    At temperature:      ', row[4])
print('\n\n')

# Get user input to determine how long job should be
while True:
    cookhour = int(input('Enter the number of hours that you want to cook (0-12): '))
    if cookhour < 0 or cookhour > 12:
        errmsgslow('Invalid selection. Please try again...')
        continue
    cookmin = int(input('Enter the number of minutes that you want to cook (0-59): '))
    if cookmin < 0 or cookmin > 59:
        errmsgslow('Invalid selection. Please try again...')
        continue
    if cookhour == 0 and cookmin == 0:
        errmsgslow('You cannot cook something for 0 hours & 0 minutes! Please try again...')
        continue
    response = input('You entered ' + str(cookhour) + ' hours and ' + str(cookmin) + ' minutes. Is this correct? [Y/N] ')
    if response.lower() == 'y':
        break
print('\n\n')

# Prompt before continuing with the job
while True:
    response = input('Enter \'y\' when you are ready to start your job or \'x\' to exit without cooking. ')
    if response.lower() == 'x':
        print('You have chosen to exit without cooking.')
        cleanexit(0)
    elif response.lower() == 'y':
        break
print('\n\n')

# Update job_info row with start time
start = datetime.now()
starttime = dbdate(start)
query('update job_info set starttime = (%s) where id = (%s)', starttime + jobid, '', True)

# Calculate job run time
cookdelta = timedelta(hours=cookhour, minutes=cookmin)
cooktime = dbnumber((cookhour * 60) + cookmin)
end = start + cookdelta
endtime = dbdate(end)
query('update job_info set endtime = (%s), cookminutes = (%s) where id = (%s)', endtime + cooktime + jobid, '', True)
print('Your job is going to cook for ' + str(cookhour) + ' hour(s) and ' + str(cookmin) + ' minute(s). It will complete at ' + endtime[0] + '.')

# Main cooking loop
fractmin = 15 # After how many seconds should I log temp to database?
currdelta = timedelta(seconds=fractmin) # How often it should log data while cooking
countdown = 0
if raspi:
    powertail(True)
while True:
    currtime = datetime.now()
    if currtime >= start + currdelta:
        current = dbdate(currtime)
        if raspi and therm_sens: # If running RPi & thermal sensor is present
            temp_cen, temp_far = gettemp() # Read temperature
            temp_c = dbnumber(temp_cen) # Convert to tuple
            temp_f = dbnumber(temp_far) # Convert to tuple
            query('insert into job_data (job_id, moment, temp_c, temp_f) \
                values ((%s), (%s), (%s))',
                jobid + current + temp_c + temp_f, '', True)
        else: # If running on test, then don't read temperature
            query('insert into job_data (job_id, moment) \
                values ((%s), (%s), (%s))',
                jobid + current, '', True)
        start = datetime.now()
        countdown += (fractmin / 60)
        timeleft = int(cooktime[0]) - countdown
        if raspi and therm_sens:
            print('Job has been active for ' + str(countdown) + ' minutes.')
            print('There are ' + str(timeleft) + ' minutes left.')
            print('The current temperature is ' + str(temp_cen) + ' degrees C.')
        else:
            print('Job has been active for ' + str(countdown) + ' minutes and there are ' + str(timeleft) + ' minutes left.')
    if raspi and currtime >= end: # Powertail off & stop if RasPi
        powertail(False)
        break
    elif currtime >= end: # Otherwise stop when time has ended
        break

print('\n\n')
print('Job complete!')
cleanexit(0)
