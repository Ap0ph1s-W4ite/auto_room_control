# auto_room_control
Link a PO18-12C LDC to see the temperature.
===============================================
Add a LCD to see the temperature that sensor have readed.

###Software Installation

You need to install this software to use the LCD wth I2C.

```sh
$ sudo apt-get install python-dev
$ sudo apt-get install python-wxgtk2.8 python-wxtools wx2.8-i18n libwxgtk2.8-dev
$ sudo apt-get install i2c-tools
```

You need to edit the file 'raspi-blacklist.conf'.

```sh
$ sudo nano /etc/modprobe.d/raspi-blacklist.conf
```
And comment out i2c line.

Add 'i2c-dev' line.
```sh
$ sudo nano /etc/modules
```
After that, write this:
```sh
$ sudo adduser pi i2c
$ mkdir notsmb
```



