#!/usr/bin/env python
import os
import p017A
import time
import glob
import re
import subprocess
from sv3A import sv3Bus

bus = sv3Bus(0,'1','') # change to '1' to '0' for older RPi
lcd = p017A.p017(bus,56)

os.system( 'modprobe w1-gpio' )
os.system( 'modprobe w1-therm' )
base_dir = '/sys/bus/w1/devices/'
device_folder_in = glob.glob( base_dir + '28-000004e46094' )[0]
device_file_in = device_folder_in + '/w1_slave'
device_folder_out = glob.glob( base_dir + '28-0000057debdf' )[0]
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
		
def getCPUtemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    return(res.replace("temp=","").replace("'C\n",""))
	
def getCPUuse():
    return(str(os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip(\
)))

while True:
	tempin = read_temp_in()
	tempout = read_temp_out()
	cputemperature = getCPUtemperature()
	usecpu = getCPUuse()
	lcd.cls()
	lcd.rc(0,1)
	lcd.lcd("TEMP. EXTERIOR")
	lcd.rc(1,4)
	lcd.lcd(tempout)
	lcd.lcd(" C")
	time.sleep(5)
	lcd.cls()
	lcd.rc(0,1)
	lcd.lcd("TEMP. INTERIOR")
	lcd.rc(1,4)
	lcd.lcd(tempin)
	lcd.lcd(" C")
	time.sleep(5)
	lcd.cls()
	lcd.rc(0,0)
	lcd.lcd("TEMPERATURA CPU")
	lcd.rc(1,5)
	lcd.lcd(cputemperature)
	lcd.lcd(" C")
	time.sleep(5)
	lcd.cls()
	lcd.rc(0,3)
	lcd.lcd("USO DO CPU")
	lcd.rc(1,5)
	lcd.lcd(usecpu)
	lcd.lcd("%")
	time.sleep(5)