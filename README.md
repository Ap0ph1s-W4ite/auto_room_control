# Auto_Room_Control
Automate your room. With this project you can automatize your room. A room is a place used to rest and sleep, not to work or open the window, NO! Your just need to rest and sleep.

The objective for this project is to control your room temperature, open the window, turn on/off the light. But, how? On a smartphone, internet, pc or just when the sensor detect your presence. Your imagination is the limit.

=======================================================
V1.0

- Added temp_control.py

  - File that will control GPIO from the Raspberry Pi according to the temperature readed from the sensor (DS18B20)

- Added temp_data.py

  - This file, through your terminal, will show the temperature readed from the sensor.
  
V1.1
- temp_data.py updated.
- temp_control.py updated
- Added LCD Suport.
  - You can use a LCD qith a P017 Chip to see temperature and usage from CPU.

=============================================
###Installation


First step is to update your raspberry pi.

```sh
$ sudo apt-get update
$ sudo apt-get upgrade
```
We will use DS18B20 to get the temperature, that means, we need to see if they are working.
To do that just execute the commands above.

```sh
$ cd /sys/bus/w1/devices/
$ ls
```

If you get values, it's working. Good!!

But what are that values? Sensors IDs, simple.

Now you have the IDs, you need to download the files from the repository.

```sh
$ cd
$ git clone git://github.com/adrianobrum/auto_room_control.git
$ cd auto_room_control
```

But the files that you downloaded are with my IDs. We will edit "temp_data.py" file, and add your IDs, if you just have one sensor you need to edit "temp_data_1.py"

How to edit the file?

```sh
device_folder_in = glob.glob( base_dir + 'ID1' )[0]
device_file_in = device_folder_in + '/w1_slave'
device_folder_out = glob.glob( base_dir + 'ID2' )[0]
device_file_out = device_folder_out + '/w1_slave'
```
Just need to clear the ID1 and ID2. Then you paste your sensor ID.

Now we need to edit the control temperature file, "temp_control.py".
```sh
os.system( 'modprobe w1-gpio' )
os.system( 'modprobe w1-therm' )
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob( base_dir + 'ID1' )[0]
device_file = device_folder + '/w1_slave'
```

You just need to do the same, again!

But, you need to edit your GPIO, the port that you have your relay connected.
```sh
while True:
    logger.debug('IN_WHILE: Temperatura lida.')
    temp_c1 = read_temp()
    logger.debug('IN_WHILE')
    if boss == 0:
        logger.debug('IN_WHILE: Variavel BOSS nula.')
        while (temp_c1 <= 22): #temperature 22C
            logger.info('Temperatura inferior a 22 C.')
            temp_c1 = read_temp()
            ledMode( 17, GPIO.HIGH if temp_c1 <= 22 else GPIO.LOW ) #GPIO17 - temperature 22C - on
            ledMode( 18, GPIO.HIGH if temp_c1 <= 21 else GPIO.LOW ) #GPIO18 - temperature 21C - on
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
         while (temp_c1 <= 21): #temperature 21C
             logger.info('Temperatura inferior a 21 C.')
             temp_c1 = read_temp()
             ledMode( 17, GPIO.HIGH if temp_c1 <= 22 else GPIO.LOW ) #GPIO17 - temperature 22C - on
             ledMode( 18, GPIO.HIGH if temp_c1 <= 21 else GPIO.LOW ) #GPIO18 - temperature 21C - on
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
```
Just change "17" and "18" to your GPIO port. The numbers "22" and "21" are the temperatures, I have 2 radiators, but if you just have one, you can eliminate the line that you don't need. If you don't know what to delete, just use the "#" to guide you.


The logger it's just to see a log file, if you want to use it, please translate to your languge, they are in portuguese.

To see the logs you need to create a folder.
```sh
$ mkdir logs
```

If you see a error, or something else, please contribute to fix. :)

