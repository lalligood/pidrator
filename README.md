## Overview ##
Using a Raspberry Pi, I want to be able to control & monitor either a slow cooker or food dehydrator. To ensure best results, a digital temperature sensor  & PostgreSQL database are configured so I can log data about each cooking task.

The Raspberry Pi will be controlled one of two ways: either a web interface for remote access and/or a GUI (access by a screen hardwired to the Raspberry Pi). Since I am new to programming with python, I am trying to leave my options open but will reassess this decision later in the project.

## Hardware & Software Needed ##
* Raspberry Pi (based on the scope of this project, any Pi should be acceptable)
* USB Wifi adapter
* High-speed (Class 10 preferred) SD/MicroSD card
* high temp waterproof DS18B20 Digital temperature sensor (purchased from Adafruit)
* Powertail 2 (purchased from Adafruit)
* Debian-based Linux distro for Rapsberry Pi (I prefer Raspbian)
* Python version 3.4+
* PostgreSQL version 9.1+
* RPi.GPIO python class (for communicating with GPIO pins on Raspberry Pi)
* psycopg2 python class (for interacting with PostgreSQL database)
* TBD: A web interface requires a http (or https) server, ergo Apache or nginx. PHP will then be required for interacting with the database.
* TBD: If a GUI is ever implemented, some kind of screen & input method will be required. (The official touchscreen display was recently released & would be an excellent candidate for this project.)

## Project Goals ##
1. **Ease of use.** If it's not easy to use, no one will want to use it. Everything should be as obvious as possible & contribute to that goal.
2. **Stability.** Using well-proven programming & database tools, it shouldn't require any extraordinary effort to make a stable application. However, it's possible to screw it up so I need to be vigilant in the execution of my code.
3. **Web interface.** The Raspberry Pi may require interacting directly with it to execute the jobs. At a minimum, the web interface is how I would like to monitor & display graphs of the progress of any previous cooking job(s). I am definitely open to exploring the possibility of using a web interface to control all aspects of the cooking job(s).
4. **Local interface.** The Raspberry Pi Foundation just released (Sep 2015) a 7" touchscreen display that attaches directly to the Pi. Depending on any progress made with the web interface, a local (only) GUI might be designed for controlling the cooking job(s).
5. **Notifications.** python can send messages via email using SMTP or via SMS. The idea of being notified periodically (or in case of job failure) is desirable.
6. **Security Concerns** Since there is a high chance of being able to control this device through a web interface, I'm taking a cautious approach to security. Thankfully setting up password encryption on the PostgreSQL database is a piece of cake. It uses Blowfish encryption & salts the encrypted password so that even instances where 2 different users use the same password, they will be unique (unlike password created with a MD5 hash). And the python code enforces a minimum password length of 8 characters.
