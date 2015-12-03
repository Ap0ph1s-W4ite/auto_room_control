#!/usr/bin/env python
# SV3 for SV3 type devices
# October 2013 Version 1.0

import serial
import sys
import os
I2C = 0
SERIAL = 1
VERSION = 1
ACK = '\006'
NACK = '\025'
IACK = '\076' # inverted ACK

# Use in the form
# >>> from sv3A import sv3Bus, sv3
# >>> bus = sv3Bus(1,"COM14",9600)
# >>> bus.list() # list all device addresses on the bus
# >>> device = sv3(bus,'h') # accessto sv3 commands for that device
# >>> device.ID() # print device id
# OR it is likely that sv3 will be a parent class of a device so
# >>> device = p015(bus,'h')
# >>> device.ID()

# ******************************************************************************
# Connects to a bus - this could be serial, serial for I2C or I2C. The bus is
# passed to an instance of a particular class
# Example:
# bus = sv3Bus(1,'COM5',baud) # windows serial
# bus = sv3Bus(1,'/dev/ttyAMA0',baud) # rpi serial
# bus = sv3Bus(0,'COM5','') # windows serial using BV4221
# bus = sv3Bus(0,'0','') # rpi bus 0 i2c
# ******************************************************************************
class sv3Bus:
    """Establish bus, either serial (bustype=1) or I2C (bustype=0)
       for sv3 communications
       bus = sv3Bus(bustype,link,rate)
       bustype = 1 for serial and 0 for i2c
       Windows:
            Serial: link = com port name where sv3 device is e.g. "COM5"
            I2C: link =  com port name where BV4221 device is e.g. "COM5"
            rate: Baud rate
       POSIX:
            Serial: link = com port name where sv3 device is e.g. "/dev/tty"
            Serial: rate = Baud rate
            I2C: link is name of I2C bus probably 0 or 1
            I2C: rate = ''
    """
    bt = None # determines serial or i2c
    com = None # communication channel
    def __init__(self,bustype, port, devicebaud):
        self.bt = bustype
        if int(self.bt) == SERIAL:
            # serial
            try:
                sp = serial.Serial(port, int(devicebaud), timeout=.05, stopbits=1, parity='N' )
            except:
                msg = 'Cant open comport,'+str(port)
                print msg
            else:
                self.com = sp
        if int(self.bt) == I2C:
            if os.name == 'nt':
                try:
                    from bv4221_i2c import By2cbus
                    bus = By2cbus(port,int(devicebaud))
                except:
                    print "Platform Windows, unable to open COM "+PORT+" to connect\nthe BV4221_V2"
                else:
                    self.com = bus
            if os.name == 'posix':
                try:
                    from notsmb import notSMB
                    bus = notSMB(int(port)) # set default to i2c channel 0
                except:
                    print "Platform POSIX, unable to open I2C bus 0\nHas notsmb been installed?"
                else:
                    self.com = bus

    # --------------------------------------------------------------------------
    # sde - serial data exchange
    # This is the only function needed for reading and writingto SV3. It is
    # similar to spi in that there is always an input and output even if one
    # or the other is not required.
    # Use:
    # The cmd must be the full command including the address and \r at the end
    # Example: s = sv3(sp,"aD\r") # get device ID from device with an address 'a'
    # Returns:
    # 1) NACK on an invalid input or if device does not exist
    # 2) The value returned or just ACK
    # --------------------------------------------------------------------------
    def sde(self,cmd):
        k = ''
        v = ''
        # send command
        self.com.flushInput()
        self.com.write(cmd)
        #print "sending:",cmd # debug
        # return value
        while k != ACK:
            k = self.com.read(1)
            if k == ACK: # all done
                if len(v) == 0:
                    v = ACK
                break
            else:
                if len(k) == 0:
                    v = ACK
                    break
                else:
                    v = v + k
        return v

    # --------------------------------------------------------------------------
    # return a list of all devices addresses the serial bus
    # Automatically detects and corrects for inversion
    # --------------------------------------------------------------------------
    def detect(self):
        if self.bt ==SERIAL:
            rl = []
            for j in range(97,123):
                self.com.flushInput()
                self.com.write(chr(j)+"H\r")
                s = self.com.read(1)
                # check for inversion and correct
                if s == IACK:
                    self.com.write(chr(j)+"I\r")
                    s = ACK
                if s == ACK:
                    rl.append(str(j))
            return rl
        else:
            return self.com.detect()

    # --------------------------------------------------------------------------
    # Retruns device ID
    # This has some error checking since it is the most likely to be used first
    # Needed to be here to get a list of device details on th bus
    # --------------------------------------------------------------------------
    def ID(self,adr):
        if self.bt == SERIAL:
            id = self.sde(adr+"D\r")
            if id == ACK:
                return 0
            else:
                return int(id)
        else:
            v = self.com.i2c(adr,[0xa1],2)
            rv = int(v[0])*256
            rv += int(v[1])
            return rv

    # --------------------------------------------------------------------------
    # Retruns firmware version, returns 2 integers major, minor
    # --------------------------------------------------------------------------
    def FW(self,adr):
        if self.bt == SERIAL:
            s = self.sde(adr+"V\r")
            return s.rsplit(".")

        else:
            # i2c needs to return string list
            v = self.com.i2c(adr,[0xa0],2)
            rv = [str(v[0]),str(v[1])]
            return rv

    # --------------------------------------------------------------------------
    # lists address, id and firemware as a list or an empty list if address
    # does not exist on bus
    # --------------------------------------------------------------------------
    def list(self,adr):
        rv = []
        id = str(self.ID(adr))
        if int(id) != 0:
            rv.append(adr)
            rv.append(id)
            fw = self.FW(adr)
            rv.append(fw[0]+"."+fw[1])
        return rv
        
    # --------------------------------------------------------------------------
    # just checks to seeif a particular address is still alive, returns 1 if so
    # and 0 if no device found
    # --------------------------------------------------------------------------
    def check(self,adr):
        rv = 0
        list = self.detect()
        if self.bt == SERIAL:
            if chr(adr) in list:
                rv = 1
        if self.bt == I2C:
            if adr in list:
                rv = 1
        return rv

    # --------------------------------------------------------------------------
    # only meaningfull if serial port used
    # --------------------------------------------------------------------------
    def close(self):
        if self.bt == SERIAL:
            self.com.close()
        elif os.name == 'nt':
            # I2C Windows uses a com port to drive the BV4221
            self.com.close()


    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def version(self):
        return VERSION


# ******************************************************************************
# Class that links a particular device to the bus
# ******************************************************************************
class sv3:
    """ SV3 class applies to all SV3 devices
        busType = 1 for serial
        com is obtained form getBus()
        address is either i2c address or serial address
    """
    bus = None   # set to communication channel
    adr = None # address is the address of the device
    def __init__(self,bus,address):
        self.bus = bus # communication instance
        self.adr = address # address of device for this instance

    # --------------------------------------------------------------------------
    # Write to eeprom, one byte at a time
    # --------------------------------------------------------------------------
    def eeWrite(self,eeadr,data):
        if self.bus.bt == SERIAL:
            self.bus.sde(self.adr+"W"+str(eeadr)+","+str(data)+"\r")
        else:
            #i2c
            self.bus.i2c(self.adr,[0x91,eeadr,data],0)

    # --------------------------------------------------------------------------
    # read from eeprom, will return a list
    # --------------------------------------------------------------------------
    def eeRead(self,start,lenght):
        if self.bus.bt == SERIAL:
            s = self.bus.sde(self.adr+"R"+str(start)+","+str(lenght)+"\r")
            return s.rsplit(",")
        else:
            # i2c
            rl = []
            for j in range(start,start+length):
                v = self.bus.i2c(self.adr,[0x90,j],1)
                rl.append(str(v[0]))
            return rl

    # --------------------------------------------------------------------------
    # Retruns device ID
    # This has some error checking since it is the most likely to be used first
    # --------------------------------------------------------------------------
    def ID(self):
        return self.bus.ID(self.adr)

    # --------------------------------------------------------------------------
    # Retruns firmware version, returns 2 integers major, minor
    # --------------------------------------------------------------------------
    def FW(self):
        return self.bus.FW(self.adr)

    # --------------------------------------------------------------------------
    # Soft reset
    # --------------------------------------------------------------------------
    def reset(self):
        if self.bus.bt == SERIAL:
            self.bus.sde(self.adr+"C\r")

        else:
            self.bus.com.i2c(self.adr,[0x95],0)


