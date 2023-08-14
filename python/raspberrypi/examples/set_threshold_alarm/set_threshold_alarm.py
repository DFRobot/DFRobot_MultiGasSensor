# -*- coding: utf-8 -*
'''
  @file  set_threshold_alarm.py
  @brief Set sensor threshold alarm
  @n Experimental mode: connect sensor communication pin to the main controller and burn, connect BCM pin 18 to pin ALA of the sensor
  @n Communication mode select, DIP switch SEL: 0: I2C, 1: UART
  @n Group serial number         Address in the group
  @n A0 A1 DIP level 00    01    10    11
  @n 1            0x60  0x61  0x62  0x63
  @n 2            0x64  0x65  0x66  0x67
  @n 3            0x68  0x69  0x6A  0x6B
  @n 4            0x6C  0x6D  0x6E  0x6F
  @n 5            0x70  0x71  0x72  0x73
  @n 6 (Default address group) 0x74  0x75  0x76  0x77 (Default address)
  @n 7            0x78  0x79  0x7A  0x7B
  @n 8            0x7C  0x7D  0x7E  0x7F
  @n @n I2C address select, default to 0x77, A1 and A0 are grouped into 4 I2C addresses.
  @n             | A0 | A1 |
  @n             | 0  | 0  |    0x74
  @n             | 0  | 1  |    0x75
  @n             | 1  | 0  |    0x76
  @n             | 1  | 1  |    0x77   default i2c address   
  @n Experimental phenomenon: when the data obtained by sensor exceeds the set threshold, the ALA pin of the sensor will output high level
  @copyright   Copyright (c) 2010 DFRobot Co.Ltd (http://www.dfrobot.com)
  @license     The MIT License (MIT)
  @author      PengKaixing(kaixing.peng@dfrobot.com)
  @version     V2.0
  @date        2021-03-28
  @url         https://github.com/DFRobot/DFRobot_MultiGasSensor
'''

import sys
import os
import time
import RPi.GPIO as GPIO

#Alarm pin
pin = 18

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from DFRobot_MultiGasSensor import *

'''
  ctype=1:UART
  ctype=0:IIC
'''
ctype=0

if ctype==0:
  I2C_1       = 0x01               # I2C_1 Use i2c1 interface (or i2c0 with configuring Raspberry Pi) to drive sensor
  I2C_ADDRESS = 0x77               # I2C Device address, which can be changed by changing A1 and A0, the default address is 0x77
  gas = DFRobot_MultiGasSensor_I2C(I2C_1 ,I2C_ADDRESS)
else:
  gas = DFRobot_MultiGasSensor_UART(9600)

GPIO.setmode(GPIO.BCM)
GPIO.setup(pin,GPIO.IN)

def setup():
  #Mode of obtaining data: the main controller needs to request the sensor for data
  while (False == gas.change_acquire_mode(gas.PASSIVITY)):
    print("wait acquire mode change!")
    time.sleep(1)
  print("change acquire mode success!")
  while (False==gas.set_threshold_alarm(gas.ON,180)):
    print ("set alarm ERROR!")
    time.sleep(1)
  
def loop():
  gas.read_gas_concentration()
  if GPIO.input(pin)==0:
    print ("warning!!!")
  else:
    print ("nolmal!!!")
  time.sleep(1)  

if __name__ == "__main__":
  setup()
  while True:
    loop()
