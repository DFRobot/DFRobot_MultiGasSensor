/*!
  * @file  readTemp.ino
  * @brief Get the current board temperature of the sensor
  * @n Experimental mode: connect sensor communication pin to the main controller and burn
  * @n Communication mode select, DIP switch SEL: 0: I2C, 1: UART
  * @n Group serial number         Address in the group
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
  * @n Experimental phenomenon: view the current board temperature through serial port printing
  * @copyright   Copyright (c) 2010 DFRobot Co.Ltd (http://www.dfrobot.com)
  * @license     The MIT License (MIT)
  * @author      PengKaixing(kaixing.peng@dfrobot.com)
  * @version     V1.0
  * @date        2021-03-28
  * @url         https://github.com/DFRobot/DFRobot_MultiGasSensor
*/
#include "DFRobot_MultiGasSensor.h"

//Turn on by default, using I2C communication at the time, switch to software serial port communication after turning off
//#define I2C_COMMUNICATION

#ifdef  I2C_COMMUNICATION
#define I2C_ADDRESS    0x77
  DFRobot_GAS_I2C gas(&Wire ,I2C_ADDRESS);
#else
/* ---------------------------------------------------------------------------------------------------------------------
 *    board   |             MCU                | Leonardo/Mega2560/M0 |    UNO    | ESP8266 | ESP32 |  microbit  |   m0  |
 *     VCC    |            3.3V/5V             |        VCC           |    VCC    |   VCC   |  VCC  |     X      |  vcc  |
 *     GND    |              GND               |        GND           |    GND    |   GND   |  GND  |     X      |  gnd  |
 *     RX     |              TX                |     Serial1 TX1      |     5     |   5/D6  |  D2   |     X      |  tx1  |
 *     TX     |              RX                |     Serial1 RX1      |     4     |   4/D7  |  D3   |     X      |  rx1  |
 * ----------------------------------------------------------------------------------------------------------------------*/
/* Baud rate cannot be changed  */
  #if defined(ARDUINO_AVR_UNO) || defined(ESP8266)
    SoftwareSerial mySerial(4, 5);
    DFRobot_GAS_SoftWareUart gas(&mySerial ,9600);
  #elif defined(ESP32)
    DFRobot_GAS_HardWareUart gas(&Serial1 ,9600 ,/*rx*/D2 ,/*tx*/D3);
  #else
    DFRobot_GAS_HardWareUart gas(&Serial1 ,9600);
  #endif
#endif

void setup() {
  //Serial port init for viewing printing output
  Serial.begin(115200);
  
  //Sensor init, init serial port or I2C, depending on the communication mode currently used
  while(!gas.begin())
  {
    Serial.println("NO Deivces !");
    delay(1000);
  }

  //Mode of obtaining data: the main controller needs to request the sensor for data
  while (!gas.changeAcquireMode(gas.PASSIVITY))
  {
    delay(1000);
  }
  Serial.println("change acquire mode success!");
}

void loop() {
  /**
   *Print the board temperature as float type
   *Print with 1s delay each time
   */
  Serial.print("The board temperature is: ");
  Serial.print(gas.readTempC());
  Serial.println(" ℃");
  Serial.println();
  delay(1000);
}