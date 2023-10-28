# -*- coding: utf-8 -*
""" 
  @file DFRobot_MultiGasSensor.py
  @note DFRobot_MultiGasSensor Class infrastructure, implementation of underlying methods
  @copyright   Copyright (c) 2010 DFRobot Co.Ltd (http://www.dfrobot.com)
  @license     The MIT License (MIT)
  @author      [PengKaixing](kaixing.peng@dfrobot.com)
  @version  V2.0
  @date  2021-03-31
  @url https://github.com/DFRobot/DFRobot_MultiGasSensor
"""
import serial
import time
import smbus
import spidev
import os
import math
import RPi.GPIO as GPIO
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)  #Display all the print information
#logger.setLevel(logging.FATAL)#Use this option if you don't want to display too many prints but only printing errors
ph = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - [%(filename)s %(funcName)s]:%(lineno)d - %(levelname)s: %(message)s")
ph.setFormatter(formatter) 
logger.addHandler(ph)

I2C_MODE  = 0x01
UART_MODE = 0x02

sendbuf = [0]*9  
recvbuf = [0]*9
def fuc_check_sum(i,ln):
  '''!
    @brief CRC check function
    @param i  CRC original data list
    @param ln Length
    @return CRC check value
  '''
  tempq=0
  for j in range(1,ln-1):
    tempq+=i[j]
  tempq=(((~tempq)&0xff)+1)
  return tempq

def clear_buffer(buf,length):
  '''!
    @brief List values are reset
    @param buf List to be cleared
    @param length Length
  '''
  for i in range(0,length):
    buf[i]=0


class DFRobot_GasType:
  '''!
    @brief Enumerates all known sensor types. DFRobot_MultiGasSensor.gastype
    @n     will be set to one of these.
  '''
  O2  = "O2"
  CO  = "CO"
  H2S = "H2S"
  NO2 = "NO2"
  O3  = "O3"
  CL2 = "CL2"
  NH3 = "NH3"
  H2  = "H2"
  HCL = "HCL"
  SO2 = "SO2"
  HF  = "HF"
  PH3 = "PH3"
  UNKNOWN = ""


class DFRobot_MultiGasSensor(object):
  '''!
    @brief This is a sensor parent class which can be used in complex environments to detect various gases.
    @details To detect gases like O2, CO, H2S, NO2, O3, CL2, NH3, H2, HCL, 
    @n       SO2, HF, PH3, which is achieved by just switching corresponding probes.
    @n       Meanwihle, it supports gas high/low threshold alarm.
    @n       Function
  '''  
  INITIATIVE =  0x03
  PASSIVITY  =  0x04
  O2         =  0x05
  CO         =  0x04
  H2S        =  0x03
  NO2        =  0x2C
  O3         =  0x2A
  CL2        =  0x31
  NH3        =  0x02
  H2         =  0x06
  HCL        =  0X2E
  SO2        =  0X2B
  HF         =  0x33
  PH3        =  0x45
  GASCON     =  0x00
  GASKIND    =  0x01
  ON         =  0x01
  OFF        =  0x00
  gasconcentration = 0.0 # Raw, uncorrected sensor measurement.
  gastype       =    ""
  gasunits      =    ""
  temp          =    0.0
  tempSwitch = OFF
  
  def __init__(self ,bus ,Baud):
    if bus != 0:
      self.i2cbus = smbus.SMBus(bus)
      self.__uart_i2c = I2C_MODE
    else:
      self.ser = serial.Serial("/dev/ttyAMA0" ,baudrate=Baud,stopbits=1)
      self.__uart_i2c = UART_MODE
      if self.ser.isOpen == False:
        self.ser.open()
        
  def __getitem__(self, k):
    if k == recvbuf:
      return recvbuf


  def __set_gastype(self, probe_type):
    '''!
      @brief   Sets instance gas type and units based on type read from sensor.
      @param probe_type Byte received from sensor indicating sensor type.
    '''
    if probe_type == self.O2:
      self.gastype = DFRobot_GasType.O2
      self.gasunits = "%%"
    elif probe_type == self.CO:
      self.gastype = DFRobot_GasType.CO
      self.gasunits = "ppm"
    elif probe_type == self.H2S:
      self.gastype = DFRobot_GasType.H2S
      self.gasunits = "ppm"
    elif probe_type == self.NO2:
      self.gasunits = "ppm"
      self.gastype = DFRobot_GasType.NO2
    elif probe_type == self.O3:
      self.gasunits = "ppm"
      self.gastype = DFRobot_GasType.O3
    elif probe_type == self.CL2:
      self.gasunits = "ppm"
      self.gastype = DFRobot_GasType.CL2
    elif probe_type == self.NH3:
      self.gasunits = "ppm"
      self.gastype = DFRobot_GasType.NH3
    elif probe_type == self.H2:
      self.gastype = DFRobot_GasType.H2
      self.gasunits = "ppm"
    elif probe_type == self.HCL:
      self.gastype = DFRobot_GasType.HCL
      self.gasunits = "ppm"
    elif probe_type == self.SO2:
      self.gastype = DFRobot_GasType.SO2
      self.gasunits = "ppm"
    elif probe_type == self.HF:
      self.gastype = DFRobot_GasType.HF
      self.gasunits = "ppm"
    elif probe_type == self.PH3:
      self.gastype = DFRobot_GasType.PH3
      self.gasunits = "ppm"
    else:
      self.gastype =DFRobot_GasType.UNKNOWN
      self.gasunits = ""


  def __adc_to_temp(self, temp_ADC):
    '''!
      @brief Converts temperature ADC measurement to temperature.
      @param temp_ADC 10-bit A/D measurement from onboard temperature sensor.
    '''
    Vpd3=float(temp_ADC/1024.0)*3
    Rth = Vpd3*10000/(3-Vpd3)
    return 1/(1/(273.15+25)+1/3380.13*(math.log(Rth/10000)))-273.15


  def __temp_correction(self, Con):
    '''!
      @brief Performs temperature correction of sensor value.
      @param Con Measured value from sensor.
    '''

    # NOTE: this implementation replicates the thresholds and corrections
    # from the C++ version of the library as of commit 54e465b. The python
    # version was significantly different in many ways, resulting in different
    # results based on which library is used.

    # TODO: restructure all of the checks below to stop repeatedly checking
    # against the same tresholds over and over. This would be more efficient
    # and way more readable if all of the checks followed the pattern:
    #
    # if self.temp < threshold_1:
    #   Con = 0.0
    # elif self.temp < threshold_2:
    #   Con = some sort of correction
    # elif self.temp < theshold_3:
    #   Con = another correction
    # else:
    #   Con = 0.0
    
    # If temperature corrections not enabled, don't alter the sensor value.
    if self.tempSwitch != self.ON:
      return 0.0

    if self.gastype == DFRobot_GasType.O2:
      # No temperature dependency.
      pass

    elif self.gastype == DFRobot_GasType.CO:
      if (self.temp > -40) and (self.temp <= 20):
        Con = Con / (0.005 * self.temp + 0.9)
      elif (self.temp > 20) and (self.temp <= 40):
        Con = Con / (0.005 * self.temp + 0.9) - (0.3 *self.temp - 6)
      else:
        Con = 0.0

    elif self.gastype == DFRobot_GasType.H2S:
      if (self.temp > -20) and (self.temp <= 20):
        Con = Con / (0.005 * self.temp + 0.92)
      elif (self.temp > 20) and (self.temp <= 60):
        Con = Con / (0.015 * self.temp - 0.3);
      else:
        Con = 0.0

    elif self.gastype == DFRobot_GasType.NO2:
      if (self.temp > -20) and (self.temp <= 0):
        Con = Con / (0.005 * self.temp + 0.9) - (-0.0025 * self.temp + 0.005)
      elif (self.temp > 0) and (self.temp <= 20):
        Con = Con / (0.005 * self.temp + 0.9) - (0.005 * self.temp + 0.005)
      elif (self.temp > 20) and (self.temp <= 40):
        Con = Con / (0.005 * self.temp + 0.9) - (0.0025 * self.temp + 0.1)
      else :
        Con = 0.0

    elif self.gastype == DFRobot_GasType.O3:
      if (self.temp > -20) and (self.temp <= 0):
        Con = Con / (0.015 * self.temp + 1.1) - 0.05
      elif (self.temp > 0) and (self.temp <= 20):
        Con = Con/1.1 - (0.01 * self.temp)
      elif (self.temp > 20) and (self.temp <= 40):
        Con = Con/1.1 - (-0.005 * self.temp + 0.3)
      else:
         Con = 0.0

    elif self.gastype == DFRobot_GasType.CL2:
      if (self.temp > -20) and (self.temp <= 0):
        Con = Con / (0.015 * self.temp + 1.1) -0.0025
      elif (self.temp > 0) and (self.temp <= 20):
        Con = Con / 1.1 - 0.005 * self.temp
      elif (self.temp > 20) and (self.temp < 40):
        Con = Con/1.1 - (-0.005 * self.temp + 0.3)
      else:
        Con = 0.0

    elif self.gastype == DFRobot_GasType.NH3:
      if (self.temp > -20) and (self.temp <= 0):
        Con = Con / (0.006 * self.temp + 0.95) - (-0.006 * self.temp + 0.25)
      elif (self.temp > 0) and (self.temp <= 20):
        Con = Con / (0.006 * self.temp + 0.95) - (-0.012 * self.temp + 0.25)
      elif (self.temp > 20) and (self.temp < 40):
        Con = Con / (0.005 * self.temp + 1.08) - (-0.1 * self.temp + 2)
      else:
        Con = 0.0

    elif self.gastype == DFRobot_GasType.H2:
      if (self.temp > -20) and (self.temp <= 20):
        Con = Con / (0.0074 * self.temp + 0.7) - 5
      if (self.temp > 20) and (self.temp <= 40):
        Con = Con / (0.025 * self.temp + 0.3) - 5
      if (self.temp > 40) and (self.temp <= 60):
        Con = Con / (0.001 * self.temp + 0.9) - (0.75 * self.temp-25)
      else:
        Con = 0.0

    elif self.gastype == DFRobot_GasType.HCL:
      if (self.temp > -20) and (self.temp <= 0):
        Con = Con - (-0.0075 * self.temp - 0.1)
      elif (self.temp > 0) and (self.temp <= 20):
        Con = Con - (-0.1)
      elif (self.temp > 20) and (self.temp < 50):
        Con = Con - (-0.01 * self.temp + 0.1)
      else:
        Con = 0.0

    elif self.gastype == DFRobot_GasType.SO2:
      if (self.temp >- 40) and (self.temp <= 40):
        Con = Con / (0.006 * self.temp + 0.95)
      elif (self.temp > 40) and (self.temp <= 60):
        Con = Con / (0.006 * self.temp + 0.95) - (0.05 * self.temp - 2)
      else:
        Con = 0.0

    elif self.gastype == DFRobot_GasType.HF:
      if (self.temp > -20) and (self.temp <= 0):
        Con = Con / 1 - (-0.0025 * self.temp)
      elif (self.temp > 0) and (self.temp <= 20):
        Con = Con / 1 + 0.1
      elif (self.temp>20) and (self.temp < 40):
        Con = Con / 1 - (0.0375 * self.temp - 0.85)
      else:
        Con = 0.0

    elif self.gastype == DFRobot_GasType.PH3:
      if (self.temp > -20) and (self.temp < 40):
        Con = Con / (0.005 * self.temp + 0.9)
      else:
        Con = 0.0

    else: # Do not modify values for unknown sensors.
      Con = 0.0
      pass
    # No sensor measurements are ever below zero, so it makes little sense
    # for the corrected version to be so.
    return Con


  def analysis_all_data(self,recv):
    '''!
      @brief   The obtained data list by parsing.
      @param recv The obtained data
    '''    
    #recv[5]Indicate resolution, 0 indicate resolution is 1, 1 indicate resolution is 0.1, 2 indicate resolution is 0.01
    if(recv[5]==0):
      self.gasconcentration = (recv[2] << 8) + recv[3]
    elif(recv[5]==1):
      self.gasconcentration = 0.1*((recv[2] << 8) + recv[3])
    elif(recv[5]==2):
      self.gasconcentration = 0.01*((recv[2] << 8) + recv[3])

    # Update sensor type from info in response (byte 4).
    self.__set_gastype(recv[4])

    # Update current temperature.
    temp_ADC=(recv[6]<<8)+recv[7]
    self.temp = self.__adc_to_temp(temp_ADC)

    # Perform temperature correction of the value if enabled.
    Con = self.__temp_correction(self.gasconcentration)

    
  def change_acquire_mode(self,mode):
    '''!
      @brief Change the mode of reporting data to the main controller after the sensor has collected the gas.
      @param mode Mode select
      @n     INITIATIVE The sensor proactively reports data
      @n     PASSIVITY The sensor can report data only after the main controller sends request to it.
      @return Return whether the change of gas mode succeed
      @retval True   change success
      @retval False  change fail
    '''
    sendbuf[0]=0xff
    sendbuf[1]=0x01
    sendbuf[2]=0x78
    sendbuf[3]=mode
    sendbuf[4]=0x00
    sendbuf[5]=0x00
    sendbuf[6]=0x00
    sendbuf[7]=0x00
    sendbuf[8]=fuc_check_sum(sendbuf,8)
    self.write_data(0,sendbuf,9)
    time.sleep(0.1)
    self.read_data(0,recvbuf,9)
    if(recvbuf[2]==1):
      return True
    else:
      return False

  def read_gas_concentration(self):
    '''!
      @brief Get the gas concentration or type obtained by the sensor
      @return if data is transmitted normally, return gas concentration; otherwise, return 0xffff
    '''  
    global sendbuf
    global recvbuf    
    clear_buffer(recvbuf,9)
    sendbuf[0]=0xff
    sendbuf[1]=0x01
    sendbuf[2]=0x86
    sendbuf[3]=0x00
    sendbuf[4]=0x00
    sendbuf[5]=0x00
    sendbuf[6]=0x00
    sendbuf[7]=0x00
    sendbuf[8]=fuc_check_sum(sendbuf,8)
    self.write_data(0,sendbuf,9)
    time.sleep(0.1)
    self.read_data(0,recvbuf,9)
    if(fuc_check_sum(recvbuf,8) == recvbuf[8]):
      self.gasconcentration = ((recvbuf[2]<<8)+recvbuf[3])*1.0

      # Scale measurement based on the number of decimal places indicated
      # by the sensor.
      decimal_digits = recvbuf[5]
      if decimal_digits == 1:
        self.gasconcentration = self.gasconcentration * 0.1
      elif decimal_digits == 2:
        self.gasconcentration = self.gasconcentration * 0.01

    else: # Checksum failed.
      return 0.0

    # Update sensor type from info in response (byte 4).
    self.__set_gastype(recvbuf[4])

    # Update temperature measurement if temperature correction is enabled.
    if(self.tempSwitch == self.ON):
      self.temp = self.read_temp()

    # Perform temperature correction of the value if enabled.
    Con = self.__temp_correction(self.gasconcentration)

    return Con


  def read_gas_type(self):
    '''!
      @brief Get the gas type obtained by the sensor
      @return Gas type
      @n  O2   0x05
      @n  CO   0x04
      @n  H2S  0x03
      @n  NO2  0x2C
      @n  O3   0x2A
      @n  CL2  0x31
      @n  NH3  0x02
      @n  H2   0x06
      @n  HCL  0X2E
      @n  SO2  0X2B
      @n  HF   0x33
      @n  PH3  0x45
    '''  
    clear_buffer(recvbuf,9)
    sendbuf[0]=0xff
    sendbuf[1]=0x01
    sendbuf[2]=0x86
    sendbuf[3]=0x00
    sendbuf[4]=0x00
    sendbuf[5]=0x00
    sendbuf[6]=0x00
    sendbuf[7]=0x00
    sendbuf[8]=fuc_check_sum(sendbuf,8)
    write_data(0,sendbuf,9)
    time.sleep(0.1)
    read_reg(0,recvbuf,9)
    if(fuc_check_sum(recvbuf,8) == recvbuf[8]):
      return (recvbuf[4])
    else:
      return 0xff   
    
  def set_threshold_alarm(self,switchof,threshold):
    '''!
      @brief Set sensor alarm threshold
      @param switchof Set whether to turn on alarm function
      @n        ON    Turn on alarm function
      @n        OFF   Turn off alarm function
      @param threshold Set alarm threshold
      @param gasType Gas type
      @return Whether setting threshold alarm succeed
      @retval True   change success
      @retval False  change fail
    '''  
    global sendbuf
    global recvbuf
    if self.gastype == DFRobot_GasType.O2:
      threshold *= 10
    elif self.gastype == DFRobot_GasType.NO2:
      threshold *= 10
    elif self.gastype == DFRobot_GasType.O3:
      threshold *= 10
    elif self.gastype == DFRobot_GasType.CL2:
      threshold *= 10
    elif self.gastype == DFRobot_GasType.HCL:
      threshold *= 10
    elif self.gastype == DFRobot_GasType.SO2:
      threshold *= 10
    elif self.gastype == DFRobot_GasType.HF:
      threshold *= 10
    elif self.gastype == DFRobot_GasType.PH3:
      threshold *= 10
    global sendbuf
    global recvbuf  
    clear_buffer(recvbuf,9)
    sendbuf[0]=0xff
    sendbuf[1]=0x01
    sendbuf[2]=0x89
    sendbuf[3]=switchof
    sendbuf[4]=threshold>>8
    sendbuf[5]=threshold
    sendbuf[6]=0x00
    sendbuf[7]=0x00
    sendbuf[8]=fuc_check_sum(sendbuf,8)
    self.write_data(0,sendbuf,9)
    time.sleep(0.1)
    self.read_data(0,recvbuf,9)
    if (recvbuf[8]!=fuc_check_sum(recvbuf,8)):
      return False
    if(recvbuf[2]==1):
      return True
    else:
      return False   

  def read_temp(self):
    '''!
      @brief Get sensor onboard temperature
      @return Board temperature, unit °C
    '''
    clear_buffer(recvbuf,9)
    sendbuf[0]=0xff
    sendbuf[1]=0x01
    sendbuf[2]=0x87
    sendbuf[3]=0x00
    sendbuf[4]=0x00
    sendbuf[5]=0x00
    sendbuf[6]=0x00
    sendbuf[7]=0x00
    sendbuf[8]=fuc_check_sum(sendbuf,8)
    self.write_data(0,sendbuf,9)
    time.sleep(0.1)
    self.read_data(0,recvbuf,9)
    temp_ADC=(recvbuf[2]<<8)+recvbuf[3]
    return self.__adc_to_temp(temp_ADC)
    
  def set_temp_compensation(self,tempswitch):
    '''!
      @brief Set whether to turn on temperature compensation, values output by sensor under different temperatures are various.
      @n     To get more accurate gas concentration, temperature compensation are necessary when calculating gas concentration.
      @param tempswitch Temperature compensation switch
                   ON  Turn on temperature compensation
                   OFF Turn off temperature compensation
    '''  
    self.tempSwitch = tempswitch
    temp = self.read_temp()
    
  def read_volatage_data(self):
    '''!
      @brief Get sensor gas concentration output by original voltage, which is different from reading sensor register directly.
      @n     The function is mainly for detecting whether the read gas concentration is right.
      @return The original voltage output of sensor gas concentration
    '''
    clear_buffer(recvbuf,9)
    sendbuf[0]=0xff
    sendbuf[1]=0x01
    sendbuf[2]=0x91
    sendbuf[3]=0x00
    sendbuf[4]=0x00
    sendbuf[5]=0x00
    sendbuf[6]=0x00
    sendbuf[7]=0x00
    sendbuf[8]=fuc_check_sum(sendbuf,8)
    self.write_data(0,sendbuf,9)
    time.sleep(0.1)
    self.read_data(0,recvbuf,9)
    if (recvbuf[8] != fuc_check_sum(recvbuf, 8)):
      return 0.0
    else:
      return (((recvbuf[2] << 8) + recvbuf[3])*3.0/1024*2);

  def change_i2c_addr_group(self,group):
    '''!
      @brief Change I2C address group
      @param  group The group number that the sensor is supposed to be
    '''   
    global sendbuf
    global recvbuf
    clear_buffer(recvbuf,9)
    sendbuf[0]=0xff
    sendbuf[1]=0x01
    sendbuf[2]=0x92
    sendbuf[3]=group
    sendbuf[4]=0x00
    sendbuf[5]=0x00
    sendbuf[6]=0x00
    sendbuf[7]=0x00
    sendbuf[8]=fuc_check_sum(sendbuf,8)
    self.write_data(0,sendbuf,9)      
    time.sleep(0.1)
    self.read_data(0,recvbuf,9)  
    if (recvbuf[8] != fuc_check_sum(recvbuf, 8)):
      return False
    else:
      return recvbuf[2]    
      

class DFRobot_MultiGasSensor_I2C(DFRobot_MultiGasSensor):

  def __init__(self ,bus ,addr):
    self.__addr = addr
    super(DFRobot_MultiGasSensor_I2C, self).__init__(bus,0)

  def data_is_available(self):
    '''
      * @brief Call this function in I2C active mode to determine the presence of data on data line
      * @return Whether data from sensor is available
      * @retval True  success is Available
      * @retval False  error is unavailable
      *
    ''' 
    clear_buffer(recvbuf,9)
    sendbuf[0]=0xff
    sendbuf[1]=0x01
    sendbuf[2]=0x88
    sendbuf[3]=0x00
    sendbuf[4]=0x00
    sendbuf[5]=0x00
    sendbuf[6]=0x00
    sendbuf[7]=0x00
    sendbuf[8]=fuc_check_sum(sendbuf,8)
    self.write_data(0,sendbuf,9)
    time.sleep(0.1)
    self.read_data(0,recvbuf,9)
          
    if (recvbuf[8] == fuc_check_sum(recvbuf, 8)):
      self.analysis_all_data(recvbuf)
      return True
    else:
      return False

  def write_data(self, reg, data , length):
    '''
      @brief writes data to a register
      @param reg register address
      @param value written data
    '''  
    while 1:
      try:
        self.i2cbus.write_i2c_block_data(self.__addr ,reg ,data)
        return
      except:
        print("please check connect!")
        time.sleep(1)
        return

  def read_data(self, reg ,data,length):
    '''
      @brief read the data from the register
      @param reg register address
      @param value read data
    '''
    try:
      rslt = self.i2cbus.read_i2c_block_data(self.__addr ,reg , length)
    except:
      rslt = -1
      return -1
    
    for i in range(length):
      data[i] = rslt[i]  
    return length
    
class DFRobot_MultiGasSensor_UART(DFRobot_MultiGasSensor):
  '''
    @brief An example of an UART interface module
  '''
  def __init__(self ,Baud):
    self.__Baud = Baud
    try:
      super(DFRobot_MultiGasSensor_UART, self).__init__(0,Baud)
    except:
      print ("plese get root!")
    
  def data_is_available(self):  
    '''
      *@brief Call this function in Uart active mode to determine the presence of data on data line
      *@return Whether data from sensor is available
      *@retval  True  success is Available
      *@retval  False  error is unavailable
    '''
    if(self.read_data(0,recvbuf,9)==9):
      if(fuc_check_sum(recvbuf,8) == recvbuf[8]):
        self.analysis_all_data(recvbuf)
        return True
      else:
        return False
    else:
      return False
        
  def write_data(self, reg, data , length): 
    self.ser.write(data)
    time.sleep(1)
    
  def read_data(self, reg ,data,length):
    global recvbuf
    timenow = time.time()
    i = 0
    while(time.time() - timenow) <= 2:
      count = self.ser.inWaiting()
      if count != 0:
        recvbuf = self.ser.read(count)
        self.ser.flushInput()
        recvbuf =[ord(c) for c in recvbuf]
        return count
  
