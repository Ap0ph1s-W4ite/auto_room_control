#!/usr/bin/env python
# P017  - LCD serial and I2C
# Simple Python code
# http://www.pichips.co.uk
#
# Example:
#>>> import p017A
#>>> from sv3A import sv3Bus
#>>> bus = sv3Bus(1,'COM14',9600) # open bus for all devices
#>>> device = p017A.p017(bus,'p')
#>>> device.ID()

import sv3A
from time import sleep
I2C = 0
SERIAL = 1
ROW = [0x80,0xc0,0x94,0xd4] # usual LCD rows but not always, change as required

# ------------------------------------------------------------------------------
# serial and I2C class for ADC IC P011
# ------------------------------------------------------------------------------
class p017(sv3A.sv3):
    """P017 Serial and P012 I2C LCD Chip"""

    # --------------------------------------------------------------------------
    # Sets back light r,g,b values from 0 to 10. When using a monochrome BL
    # jts set the one that is conneted, this will normally be red
    # --------------------------------------------------------------------------
    def bl(self,r,g,b):
        # check range 1-10
        if r > 9: r = 9
        if r < 0: r = 0
        if g > 9: g = 9
        if g < 0: g = 0
        if b > 9: b = 9
        if b < 0: b = 0
        if self.bus.bt == SERIAL:
            self.bus.sde(self.adr+"b"+str(r)+","+str(g)+","+str(b)+"\r")
        else:
            self.bus.com.i2c(self.adr,[1,r,g,b],0)

    # --------------------------------------------------------------------------
    # Direct LCD command
    # --------------------------------------------------------------------------
    def cmd(self,cmd):
        if self.bus.bt == SERIAL:
            self.bus.sde(self.adr+"c"+str(cmd)+"\r")
        else:
            self.bus.com.i2c(self.adr,[2,cmd],0)

    # --------------------------------------------------------------------------
    # Print data
    # Not data can be anything as it will be converted to a string by Python
    # --------------------------------------------------------------------------
    def lcd(self,data):
        if self.bus.bt == SERIAL:
            self.bus.sde(self.adr+"d"+str(data)+"\r")
        else:
            # create a list from the data given
            s = str(data) # in case it is not a string
            list = [3] # start with the command
            for n in s:
                list.append(ord(n))
            list.append(13) # must be terminated by 13    
            self.bus.com.i2c(self.adr,list,0)

    # ==========================================================================
    # Derived functions using basic commands
    # ==========================================================================

    # --------------------------------------------------------------------------
    # sets row and column. This uses the table at the head of the file and may 
    # not apply to all LCD displays, but works for most
    # rowas are 0 to 3
    # --------------------------------------------------------------------------
    def rc(self,row,col):
        if row > 3 : row = 3
        if row < 0 : row = 0
        d = ROW[row] + col
        self.cmd(d)  

    # --------------------------------------------------------------------------
    # Clears the screen
    # --------------------------------------------------------------------------
    def cls(self):
        self.cmd(1)
        sleep(0.2)
        
    # --------------------------------------------------------------------------
    # changes cursor
    # 0 - cursor off
    # 1 - flashing
    # 2 - normal
    # --------------------------------------------------------------------------
    def cursor(self,cv):
        if cv == 0: self.cmd(12)
        if cv == 1: self.cmd(15)
        if cv == 2: self.cmd(14)
        

