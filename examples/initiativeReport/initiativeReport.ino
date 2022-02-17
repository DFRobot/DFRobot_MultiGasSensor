/*!
  * @file  initiativeReport.ino
  * @brief The sensor proactively reports all the data
  * @n Experimental mode: connect sensor communication pin to the main controller and burn
  * @n Communication mode select, DIP switch SEL: 0: I2C, 1: UART
  * @n Group serial number         address in the group
  * @n A0 A1 DIP level 00    01    10    11
  * @n 1            0x60  0x61  0x62  0x63
  * @n 2            0x64  0x65  0x66  0x67
  * @n 3            0x68  0x69  0x6A  0x6B
  * @n 4            0x6C  0x6D  0x6E  0x6F
  * @n 5            0x70  0x71  0x72  0x73
  * @n 6 (Default address group) 0x74  0x75  0x76  0x77 (Default address)
  * @n 7            0x78  0x79  0x7A  0x7B
  * @n 8            0x7C  0x7D  0x7E  0x7F
  * @n i2c address select, default to 0x77, A1 and A0 are grouped into 4 I2C addresses.
  * @n             | A0 | A1 |
  * @n             | 0  | 0  |    0x74
  * @n             | 0  | 1  |    0x75
  * @n             | 1  | 0  |    0x76
  * @n             | 1  | 1  |    0x77   default i2c address    
  * @n Experimental phenomenon: serial print all the data
  * @copyright   Copyright (c) 2010 DFRobot Co.Ltd (http://www.dfrobot.com)
  * @license     The MIT License (MIT)
  * @author      PengKaixing(kaixing.peng@dfrobot.com)
  * @version     V1.0
  * @date        2021-03-28
  * @url         https://github.com/DFRobot/DFRobot_MultiGasSensor
*/
#include "DFRobot_MultiGasSensor.h"

//Turn on by default, using I2C communication at the time, switch to UART communication after turning off
#define I2C_COMMUNICATION

#ifdef I2C_COMMUNICATION
#define I2C_ADDRESS 0x77
DFRobot_GAS_I2C gas(&Wire, I2C_ADDRESS);
#else
#if (!defined ARDUINO_ESP32_DEV) && (!defined __SAMD21G18A__)
/**
  UNO:pin_2-----RX
      pin_3-----TX
*/
SoftwareSerial mySerial(2, 3);
DFRobot_GAS_SoftWareUart gas(&mySerial);
#else
/**
  ESP32:IO16-----RX
        IO17-----TX
*/
DFRobot_GAS_HardWareUart gas(&Serial2); //ESP32HardwareSerial
#endif
#endif

void setup() {
  //Serial port init for viewing print output
  Serial.begin(115200);
  
  //Sensor init, init serial port or I2C, depending on the communication mode currently used
  while(!gas.begin())
  {
    Serial.println("NO Deivces !");
    delay(1000);
  }
  /**
   *Turn on temperature compensation: gas.ON :turn on
   *                                  gas.OFF:turn off
   */
  gas.setTempCompensation(gas.ON);

  //Mode of obtaining data: the sensor proactively reports data
  gas.changeAcquireMode(gas.INITIATIVE);
  delay(1000);
}

void loop() {
  if(true==gas.dataIsAvailable())
  {
    Serial.println("========================");
    Serial.print("gastype:");
    Serial.println(AllDataAnalysis.gastype);
    Serial.println("------------------------");
    Serial.print("gasconcentration:");
    Serial.print(AllDataAnalysis.gasconcentration);
    if (AllDataAnalysis.gastype.equals("O2"))
      Serial.println(" %VOL");
    else
      Serial.println(" PPM");
    Serial.println("------------------------");
    Serial.print("temp:");
    Serial.print(AllDataAnalysis.temp);
    Serial.println(" ℃");
    Serial.println("========================");
  }
  delay(1000);
}
