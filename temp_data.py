#!/usr/bin/env python
import os
import time
import glob
import re
import subprocess
os.system( 'modprobe w1-gpio' )
os.system( 'modprobe w1-therm' )
base_dir = '/sys/bus/w1/devices/'
device_folder_in = glob.glob( base_dir + 'ID1' )[0]
device_file_in = device_folder_in + '/w1_slave'
device_folder_out = glob.glob( base_dir + 'ID2' )[0]
device_file_out = device_folder_out + '/w1_slave'
def read_temp_raw_in():
    f = open(device_file_in, 'r')
    lines_in = f.readlines()
    f.close()
    return lines_in	
def read_temp_in():
    lines_in = read_temp_raw_in()
    while lines_in[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines_in = read_temp_raw_in()
    equals_pos = lines_in[1].find('t=')
    if equals_pos != -1:
        temp_string = lines_in[1][equals_pos+2:]
        temp_in = float(temp_string) / 1000.0
        return temp_in
def read_temp_raw_out():
    f = open(device_file_out, 'r')
    lines_out = f.readlines()
    f.close()
    return lines_out	
def read_temp_out():
    lines_out = read_temp_raw_out()
    while lines_out[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines_out = read_temp_raw_out()
    equals_pos = lines_out[1].find('t=')
    if equals_pos != -1:
        temp_string = lines_out[1][equals_pos+2:]
        temp_out = float(temp_string) / 1000.0
        return temp_out
temp_in = read_temp_in()
temp_out = read_temp_out()
ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) 
print 'Hora:{0}'.format( ts )
print 'Temperatura Interior: {0} C'.format( temp_in )
print 'Temperatura Exterior: {0} C'.format( temp_out )
