/*!
  * @file  changeSensorI2CAddr.ino
  * @brief The sensor proactively reports all the data, only i2c communication can use this demo.
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

#define I2C_ADDRESS    0x77
  DFRobot_GAS_I2C gas(&Wire ,I2C_ADDRESS);

uint8_t scan()
{
  Wire.begin();
  for(uint8_t address = 1; address < 127; address++ ) {
    Wire.beginTransmission(address);
    if (Wire.endTransmission() == 0)
      return address;
  }
  return 0xff;
}
void setup() {
  Serial.begin(115200);
  gas.setI2cAddr(scan());
  //Sensor init, init serial port or I2C, depending on the communication mode currently used
  while(!gas.begin())
  {
    Serial.println("NO Deivces !");
    delay(1000);
  }

  //Change i2c address group
  while(gas.changeI2cAddrGroup(3)==0)
  {
    Serial.println("IIC addr change fail!");
    delay(1000);
  }  
  Serial.println("IIC addr change success!");
}

void loop(){
}
