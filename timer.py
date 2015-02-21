#!/usr/bin/python

import time

start_time = time.time()
elapsed_time = time.time()
timediff = 0
print start_time, elapsed_time, timediff
while True:
	timediff = elapsed_time - start_time
	if timediff >= 10:
		print 'It\'s been 10 seconds!'
		localtime = time.asctime()
		print "Local current time :", localtime
		current_time = time.time()
		elapsed_time = time.time()
	else:
		time.sleep(1)
		print timediff
