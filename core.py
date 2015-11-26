#!/usr/bin/python3
__author__ = 'lalligood'

import getpass
import logging
import platform
import psycopg2
from psycopg2 import extras
import sys
import time

# Enable some functionality ONLY if raspi!
raspi = platform.machine().startswith('armv')

class DBconn:
    # Following is necessary for handling UUIDs with PostgreSQL
    extras.register_uuid()
    def __init__(self):
        'Declare database connection variables.'
        if raspi: # RASPI DB
            self.dbname = 'pi'
            self.dbuser = 'pi'
            self.dbport = 5432
        else: # NON-RASPI TEST DB
            self.dbname = 'postgres'
            self.dbuser = 'lalligood'
            self.dbport = 5433

        # Open connection to database.
        try:
            self.conn = psycopg2.connect(database=self.dbname, user=self.dbuser, port=self.dbport)
            self.cur = self.conn.cursor()
            logging.info('Connected to database successfully')
        except psycopg2.Error as dberror:
            logging.critical('UNABLE TO CONNECT TO DATABASE. Is it running?')
            self.clean_exit(1)

    def query(self, SQL, params=None, commit=False, fetch=None):
        '''General purpose query submission. Can be used for SELECT, UPDATE, INSERT,
        or DELETE queries, with or without parameters in query.

        Commit is boolean to commit transaction. Required True for UPDATE, INSERT,
        or DELETE. Not needed (False) for SELECT.

        Fetch parameter: 'all' returns multiple rows, 'one' returns one row,
        and any other value returns none.'''
        try:
            self.cur.execute(SQL, params)
            logging.info("Query '" + SQL + "' executed successfully.")
            if commit:
                self.conn.commit()
            if fetch == 'all':
                return self.cur.fetchall()
            elif fetch == 'one':
                return self.cur.fetchone()
        except psycopg2.Error as dberror:
            logging.error(dberror.diag.severity + ' - ' + dberror.diag.message_primary)
            logging.error('Failed query: ' + SQL)

    def clean_exit(self, exitcode):
        'Closes database connection & attempts to exit gracefully.'
        self.cur.close()
        self.conn.close()
        if exitcode == 0: # Log as info when closing normally
            logging.info('Shutting down application with exit status ' + str(exitcode) + '.')
        else: # Log as error when closing abnormally
            logging.error('Shutting down application prematurely with exit status ' + str(exitcode) + '.')
        logging.shutdown()
        sys.exit(exitcode)

def verify_python_version():
    'Verify that script is running python 3.x.'
    (major, minor, patchlevel) = platform.python_version_tuple()
    if int(major) < 3: # Verify running python3
        logging.error('pidrator is written to run on python version 3.')
        logging.error("Please update by running 'sudo apt-get install python3'.")
        sys.exit(1)
    elif raspi and getpass.getuser() != 'root': # RasPi should only run as root
        logging.error('For proper functionality, pidrator should be run as root (sudo)!')
        sys.exit(1)

def enable_pi_hardware():
    'Enable all devices attached to RaspPi GPIO.'
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

def errmsgslow(text):
    'Prints message then pauses for 2 seconds.'
    print(text)
    time.sleep(2)

def pick_list(userdb, listname, colname, tablename, ordername):
    '''Displays a list of items referred as listname from the column name
(colname) from table (tablename) & the list is ordered by ordername is desired.

It then asks if you want to add item(s) to the list, select an item from the
list, or return an error if the choice is not valid.'''
    while True:
        # Display all item(s) in list or state that the list is empty
        itemlist, itemnbr, countlist = show_pick_list(userdb, listname, colname, tablename, ordername)
        # Enter item(s) into the list
        if itemnbr == '0' or itemlist == []: # Add new item to the table
            newitem = dbinput('Enter the name of the item you would like to add: ', '')
            if len(newitem[0]) == 0: # Make sure user input is not empty
                errmsgslow('Invalid entry. Please try again...')
                continue
            confirm = input('You entered: ' + newitem[0] + '. Is that correct? [Y/N] ')
            if confirm.lower() == 'y':
                # Verify the new item does not match any existing item(s)
                isamatch = match_item_check(userdb, colname, tablename, itemlist, itemnbr, newitem)
                if isamatch:
                    continue
                # Insert new item into table
                insertrow = 'insert into ' + tablename + ' (' + colname + ') values ((%s))'
                userdb.query(insertrow, newitem, True)
                print('{} has been added to the list of {}.'.format(newitem[0], listname))
                print('Returning to list of available {}.'.format(listname))
            elif confirm.lower() == 'n':
                errmsgslow('Entry refused. Please try again...')
                continue
            else:
                errmsgslow('Invalid entry. Please try again...')
                continue
        elif int(itemnbr) < 0 or int(itemnbr) > countlist:
            errmsgslow('Invalid selection. Please try again...')
            continue
        else: # Find the item in the list
            count = 0
            for x in itemlist: # Iterate & find selected value
                count += 1
                if count == itemnbr:
                    itemname = x
                    print('You selected: {}.'.format(itemname[0]))
                    selectid = 'select id from ' + tablename + ' where ' + colname + ' = (%s)'
                    itemid = userdb.query(selectid, itemname, False, 'one')
                    return itemid
                    break

def show_pick_list(userdb, listname, colname, tablename, ordername):
    '''Displays item(s) in the list. If the list is empty, it returns a message
that item(s) need to be added to the list.'''
    itemnbr = ''
    order = eval('(\'' + ordername + '\', )')
    selectorder = 'select ' + colname + ' from ' + tablename + ' order by ' + ordername
    itemlist = userdb.query(selectorder, None, False, 'all')
    if itemlist == []: # Inform that table is empty
        print('No items found. Please add a new item to the {} list...'.format(listname))
    else: # Show any row(s) exist in table
        print('The following {} are available: '.format(listname))
        count = 0
        for x in itemlist: # Display list of items
            count += 1
            print('\t{}. {}'.format(count, x[0]))
        print('\t0. Add a new item to the {} list.'.format(listname))
        countlist = count
        itemnbr = input('Enter the number of the item that you want to use: ')
        return itemlist, itemnbr, countlist

def match_item_check(userdb, colname, tablename, itemlist, itemnbr, newitem):
    '''Once the user has input a new item, this verifies that it does not match
an existing item in the list.'''
    if itemlist != None:
        selectname = 'select ' + colname + ' from ' + tablename + ' where ' + colname + ' = (%s)'
        existingitem = userdb.query(selectname, newitem, False, 'one')
        if newitem == existingitem: # If existing item is found, disallow
            matchfound = True
            errmsgslow('That item already exists in the list. Please try again...')
        else:
            matchfound = False
        return matchfound

def login_menu(userdb):
    'Basic Welcome screen to login, create acct, or exit.'
    while True:
        menuopt = input('''
pidrator Menu

Select from one of the following choices:
    1. Login (must have an account)
    2. Create a new account
    x. Exit
Enter your selection: ''')
        if menuopt == '1':
            user = user_login(userdb)
            return user
            break
        elif menuopt == '2':
            user = user_create(userdb)
            return user
            break
        elif menuopt == 'x':
            print('Exiting pidrator...')
            userdb.clean_exit(0)
        else:
            errmsgslow('Invalid choice. Please try again...')

def get_job_time():
    'Get user input to determine how long job should run.'
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
        response = input('You entered {} hours and {} minutes. Is this correct? [Y/N] '.format(cookhour, cookmin))
        if response.lower() == 'y':
            break
    print('\n\n')

def confirm_job(userdb):
    'Prompt user before starting the job.'
    while True:
        response = input(r'''Enter 'y' when you are ready to start your job or 'x' to exit without cooking. ''')
        if response.lower() == 'x':
            print('You have chosen to exit without cooking.')
            userdb.clean_exit(0)
        elif response.lower() == 'y':
            break
        else:
            errmsgslow('Invalid selection. Please try again...')
    print('\n\n')

def change_pswd_prompt(userdb, user):
    'Prompt user to change password & handle (in)correct responses.'
    while True:
        response = input('Do you want to change your password? [Y/N] ')
        if response.lower() == 'y':
            changepswd(userdb, user)
            break
        elif response.lower() == 'n':
            break
        else:
            errmsgslow('Invalid selection. Please try again...')
    print('\n\n')

def dbinput(text, input_type):
    'Gets user input & formats input text for use in query as a parameter.'
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
    'Gets numeric value & formats for use in query as a parameter.'
    response = eval('(\'' + str(number) + '\', )')
    return response

def dbdate(date):
    'Gets date value & formats for use in query as a parameter.'
    response = eval('(\'' + datetime.strftime(date, date_format) + '\', )')
    return response

def user_login(userdb):
    'Handles user login by verifying that the user & password are correct.'
    badlogin = 0 # Counter for login attempts; 3 strikes & you're out
    while True:
        username = dbinput('Enter your username: ', 'user')
        pswd = dbinput('Enter your password: ', 'pswd')
        userverify = userdb.query('''select username from users
            where username = (%s)''', username, False, 'one')
        pswdverify = userdb.query('''select
            (password = crypt((%s), password)) as userpass
            from users where username = (%s)''',
            pswd + username, False, 'one')
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
            userdb.clean_exit(1)
        else: # Failed login message & try again
            errmsgslow('Username and/or password incorrect. Try again...')

def user_create(userdb):
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
        existinguser = userdb.query('''select username from users
            where username = (%s)''', username, False, 'one')
        if username == existinguser: # Make sure user doesn't already exist
            errmsgslow('That username is already in use. Please try again...')
            continue
        else: # If all conditions met, then add user
            userdb.query('''insert into users
                (username, fullname, email_address, password) values
                ((%s), (%s), (%s), crypt((%s), gen_salt('bf')))''',
                username + fullname + emailaddr + pswd, True)
            print('Your username was created successfully.')
            return username

def change_pswd(userdb, username):
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
        pswdverify = userdb.query('''select
            (password = crypt((%s), password)) as userpass from users
            where username = (%s)''', oldpswd + username, False, 'one')
        if pswdverify[0]:
            userdb.query('''update users set password = crypt((%s),
                gen_salt('bf')) where username = (%s)''',
                newpswd1 + username, True)
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

def read_temp():
    'If device is present, it will open a connection to thermal sensor.'
    if raspi:
        sensor = open(sensor_file, 'r') # Open thermal sensor "file"
        rawdata = sensor.readlines() # Read sensor
        sensor.close() # Close "file"
        return rawdata

def get_temp():
    'Reads thermal sensor until it gets a valid result.'
    if raspi:
        results = readtemp()                    # Read sensor
        while results[0].strip()[-3:] != 'YES': # Continues until result
            results = readtemp()                # is valid, just in case
        validate = results[1].find('t=')
        if validate != -1:
            parse_temp = lines[1][equals_pos + 2:]
            temp_c = round((float(parse_temp) / 1000.0), 3)
            temp_f = round((temp_c * 9.0 / 5.0 + 32.0), 3)
            return temp_c, temp_f # Return temp to 3 decimal places in C & F

def verify_pgextensions(userdb):
    '''Attempts to install all necessary PostgreSQL database extensions for the
proper operation of the pidrator.py script.'''
    extensions = {
        'uuid-ossp': 'create extension if not exists "uuid-ossp";',
        'pgcrupto': 'create extension if not exists "pgcrypto";'
        }
    for extension_name, extension_SQL in extensions.items():
        try:
            userdb.query(extension_SQL)
        except psycopg2.Error as dberror:
            logging.critical("Unable to create " + extension_name + " extension.")
            logging.critical("Run 'apt-get install postgresql-contrib-9.4' then re-run buildtables.py.")
            userdb.clean_exit(1)
        else:
            print('{} database extension installed.'.format(extension_name ))

def verify_schema(userdb):
    'Query database to see which table(s) exist.'
    schema = ('public', )
    tables = userdb.query('''select table_name from information_schema.tables
        where table_schema = (%s) order by table_name''', schema, False, 'all')
    # Convert results tuple -> list
    tables_list = []
    for table in tables:
        print('{} table found.'.format(table[0].upper()))
        tables_list.append(table[0])
    master_list = ['devices', 'foodcomments', 'foods', 'job_data', 'job_info', 'users']
    # Get difference(s) between master_list and tables_list
    results_list = set(master_list).difference(tables_list)
    if len(results_list) > 0:
        # Create any missing table(s) in the database
        for result in results_list:
            c.create_table(userdb, result)
    else:
        print('\nAll tables are present in the database. Exiting...')

def create_tables(userdb, table):
    'Create table(s) in database for pidrator if any do not exist.'
    tables = {
        'devices': '''create table devices (
            id uuid not null default uuid_generate_v4()
            , devicename text not null unique
            , createdate timestamp with time zone default now()
            , constraint devices_pkey primary key (id));''',
        'foodcomments': '''create table foodcomments (
            jobinfo_id uuid not null
            , foodcomments text
            , createtime timestamp with time zone default now());''',
        'foods': '''create table foods (
            id uuid not null default uuid_generate_v4()
            , foodname text not null unique
            , createdate timestamp with time zone default now()
            , constraint foods_pkey primary key (id));''',
        'job_data': '''create table job_data (
            id serial
            , job_id uuid
            , moment timestamp with time zone
            , temp_c double precision
            , temp_f double precision
            , constraint job_data_pkey primary key (id));''',
        'job_info': '''create table job_info (
            id uuid not null default uuid_generate_v4()
            , jobname text not null unique
            , user_id uuid
            , device_id uuid
            , food_id uuid
            , temperature_deg int
            , temperature_setting text
            , createtime timestamp with time zone default now()
            , starttime timestamp with time zone
            , endtime timestamp with time zone
            , cookminutes int
            , constraint job_info_pkey primary key (id));''',
        'users': '''create table users (
            id uuid not null default uuid_generate_v4()
            , username text not null unique
            , fullname text not null
            , email_address text not null unique
            , "password" text not null
            , createdate timestamp with time zone default now()
            , constraint users_pkey primary key (id));'''}
    for table_name, table_SQL in tables.items():
        if table_name == table:
            try:
                userdb.query(table_SQL, None, True)
            except psycopg2.Error as dberror:
                logging.critical("Unable to create " + table_name.upper() + " table.")
                logging.critical("Verify database is running and re-run buildtables.py.")
                userdb.clean_exit(1)
            else:
                print('{} table created successfully.'.format(table_name.upper()))
