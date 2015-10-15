#! python3
__author__ = 'lalligood'

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

class UserSecurity:
    # Handles user login verification & password resets
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

class PiHardware:
    # Controls hardware attached to Raspberry Pi
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
            while results[0].strip()[-3:] != 'YES': # Continues until result
                results = readtemp()                # is valid, just in case
            validate = results[1].find('t=')
            if validate != -1:
                parse_temp = lines[1][equals_pos + 2:]
                temp_c = round((float(parse_temp) / 1000.0), 3)
                temp_f = round((temp_c * 9.0 / 5.0 + 32.0), 3)
                return temp_c, temp_f # Return temp to 3 decimal places in C & F

class CreatePiTables:
    # Creates any/all database tables
    def create_devices():
        'Create DEVICES table in database if it does not exist.'
        query('create table devices (\
        id uuid not null default uuid_generate_v4()\
        , devicename text not null unique\
        , createdate timestamp with time zone default now()\
        , constraint devices_pkey primary key (id)\
        );', None, '', True)
        print("'devices' table created successfully.")

    def create_foodcomments():
        'Create FOODCOMMENTS table in database if it does not exist.'
        query('create table foodcomments (\
        jobinfo_id uuid not null\
        , foodcomments text\
        , createtime timestamp with time zone default now()\
        );', None, '', True)
        print("'foodcomments' table created successfully.")

    def create_foods():
        'Create FOODS table in database if it does not exist.'
        query('create table foods (\
        id uuid not null default uuid_generate_v4()\
        , foodname text not null unique\
        , createdate timestamp with time zone default now()\
        , constraint foods_pkey primary key (id)\
        );', None, '', True)
        print("'foods' table created successfully.")

    def create_job_data():
        'Create JOB_DATA table in database if it does not exist.'
        query('create table job_data (\
        id serial\
        , job_id uuid\
        , moment timestamp with time zone\
        , temp_c double precision\
        , temp_f double precision\
        , constraint job_data_pkey primary key (id)\
        );', None, '', True)
        print("'job_data' table created successfully.")

    def create_job_info():
        'Create JOB_INFO table in database if it does not exist.'
        query('create table job_info (\
        id uuid not null default uuid_generate_v4()\
        , jobname text not null unique\
        , user_id uuid\
        , device_id uuid\
        , food_id uuid\
        , temperature_deg int\
        , temperature_setting text\
        , createtime timestamp with time zone default now()\
        , starttime timestamp with time zone\
        , endtime timestamp with time zone\
        , cookminutes int\
        , constraint job_info_pkey primary key (id)\
        );', None, '', True)
        print("'job_info' table created successfully.")

    def create_users():
        'Create USERS table in database if it does not exist.'
        query('create table users (\
        id uuid not null default uuid_generate_v4()\
        , username text not null unique\
        , fullname text not null\
        , email_address text not null unique\
        , "password" text not null\
        , createdate timestamp with time zone default now()\
        , constraint users_pkey primary key (id)\
        );', None, '', True)
        print("'users' table created successfully.")

