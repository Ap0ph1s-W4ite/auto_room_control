#!/usr/bin/env python
import os
import time
import logging
import glob
import RPi.GPIO as GPIO
import re
import subprocess
os.system( 'modprobe w1-gpio' )
os.system( 'modprobe w1-therm' )
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob( base_dir + 'ID1' )[0]
device_file = device_folder + '/w1_slave'
GPIO.setmode( GPIO.BCM )
GPIO.setwarnings( False )
def ledMode( PiPin, mode ):
    GPIO.setup( PiPin, GPIO.OUT )
    GPIO.output( PiPin, mode )
    return
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines	
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c1 = float(temp_string) / 1000.0
        return temp_c1

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

fh = logging.FileHandler('/home/master/temp_p_room/logs/log_temp_control.txt')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

ledMode( 17, GPIO.LOW )
logger.info('GPIO 17 - Set to LOW.')

ledMode( 18, GPIO.LOW )
logger.info('GPIO 18 - Set to LOW.')

boss=0
logger.info('Variavel BOSS = 0.')

temp_c1 = read_temp()
logger.debug('OUT_WHILE: Temperatura interior lida')

while True:
    logger.debug('IN_WHILE: Temperatura lida.')
    temp_c1 = read_temp()
    logger.debug('IN_WHILE')
    if boss == 0:
        logger.debug('IN_WHILE: Variavel BOSS nula.')
        while (temp_c1 <= 22):
            logger.info('Temperatura inferior a 22 C.')
            temp_c1 = read_temp()
            ledMode( 17, GPIO.HIGH if temp_c1 <= 22 else GPIO.LOW )
            ledMode( 18, GPIO.HIGH if temp_c1 <= 21 else GPIO.LOW )
            if temp_c1 <= 22:
                logger.debug('GPIO 17 - Set to HIGH.')
            if temp_c1 <= 21:
                logger.debug('GPIO 18 - Set to HIGH.')
            if temp_c1 > 21:
                logger.debug('GPIO 18 - Set to LOW.')
            time.sleep(30)
            boss = 1
            logger.debug('IN_WHILE: Variavel BOSS positiva.')
    if (boss == 1):
         logger.debug('IN_WHILE: Variavel BOSS positiva.')
         while (temp_c1 <= 21):
             logger.info('Temperatura inferior a 21 C.')
             temp_c1 = read_temp()
             ledMode( 17, GPIO.HIGH if temp_c1 <= 22 else GPIO.LOW )
             ledMode( 18, GPIO.HIGH if temp_c1 <= 21 else GPIO.LOW )
             if temp_c1 <= 22:
                 logger.debug('GPIO 17 - Set to HIGH.')
             if temp_c1 <= 21:
                 logger.debug('GPIO 18 - Set to HIGH.')
             if temp_c1 > 21:
                 logger.debug('GPIO 18 - Set to LOW.')
             time.sleep(30)
             boss = 0
             logger.debug('IN_WHILE: Variavel BOSS nula.')
    logger.info('Temperatura superior a 22 C.')
    logger.debug('GPIO 17 - Set to LOW.')
    time.sleep(30)
