# DFRobot_MultiGasSensor
- [中文版](./README_CN.md)

Gas sensors are widely applied to many fields such as gas research, environmental detection, production safety monitoring, dissolved gas analysis, pollution source/outlet law research, detection of toxic and harmful and combustible gas, laboratory or on-site simple gas analysis and testing, etc. This Multi-gas Sensor can be used with a variety of gas probes to detect hazardous gas concentration.
![正反面svg效果图](./resources/images/DFR0784.png)

## Product Link(https://www.dfrobot.com/product-2510.html)

  SKU:SEN0465
  SKU:SEN0466
  SKU:SEN0467
  SKU:SEN0468
  SKU:SEN0469
  SKU:SEN0470
  SKU:SEN0471
  SKU:SEN0472
  SKU:SEN0473
  SKU:SEN0474
  SKU:SEN0475
  SKU:SEN0476

## Table of Contents

* [Summary](#summary)
* [Installation](#installation)
* [Methods](#methods)
* [Compatibility](#compatibility)
* [History](#history)
* [Credits](#credits)

## Summary

This Gas Sensor can be used in complex environments to detect different gas like O2, CO, H2S, 
NO2, O3, CL2, NH3, H2, HCL, SO2, HF and PH3, which is achieved by just switching corresponding probes.
Meanwihle, it supports gas high/low threshold alarm.

## Installation

To use this library download the zip file, uncompress it to a folder named DFRobot_MultiGasSensor.
Download the zip file first to use this library and uncompress it to a folder named DFRobot_MultiGasSensor.

## Methods

```C++
  /**
   * @fn begin
   * @brief Parent class init, I2C or UART init is performed in subclass function
   * @return bool type, indicating whether init succeed
   * @retval True succeed
   * @retval False failed
   */
  virtual bool begin(void) = 0;

  /**
   * @fn changeAcquireMode
   * @brief Change sensor data acquiring mode
   * @param mode Mode select
   * @n     INITIATIVE The sensor proactively reports data
   * @n     PASSIVITY The main controller needs to request data from sensor
   * @return bool type, indicating whether the setting is successful
   * @retval True succeed
   * @retval False failed
   */
  bool changeAcquireMode(eMethod_t mode);

  /**
   * @fn readGasConcentrationPPM
   * @brief Get gas concentration from sensor, unit PPM
   * @return float type, indicating return gas concentration, if data is transmitted normally, return gas concentration, otherwise, return 0.0
   */
  float readGasConcentrationPPM(void);

  /**
   * @fn queryGasType
   * @brief Query gas type
   * @return String type, indicating return gas type string
   */
  String queryGasType(void);

  /**
   * @fn setThresholdAlarm
   * @brief Set sensor alarm threshold
   * @param switchof Whether to turn on threshold alarm switch
   * @n            ON Turn on     
   * @n           OFF Turn off
   * @param threshold The threshold for starting alarm
   * @param alamethod Set sensor high or low threshold alarm
   * @param gasType   Gas type
   * @return bool type, indicating whether the setting is successful
   * @retval True succeed
   * @retval False failed
   */
  bool setThresholdAlarm(eSwitch_t switchof, uint16_t threshold, eALA_t alamethod, String gasType);

  /**
   * @fn readTempC
   * @brief Get sensor onboard temperature
   * @return float type, indicating return the current board temperature
   */
  float readTempC(void);

  /**
   * @fn setTempCompensation
   * @brief Set whether to turn on temperature compensation, values output by sensor under different temperatures are various.
   * @n     To get more accurate gas concentration, temperature compensation are necessary when calculating gas concentration.
   * @param tempswitch Whether to turn on temperature compensation
   * @n             ON Turn on temperature compensation
   * @n            OFF Turn off temperature compensation
   */
  void setTempCompensation(eSwitch_t tempswitch);

  /**
   * @fn readVolatageData
   * @brief Get sensor gas concentration output by original voltage, which is different from reading sensor register directly.
   * @n     The function is mainly for detecting whether the read gas concentration is right.
   * @param vopin Pin for receiving the original voltage output from sensor probe 
   * @return float type, indicating return the original voltage output of sensor gas concentration
   */
  float readVolatageData(uint8_t vopin);

  /**
   * @fn pack
   * @brief Pack the protocol data for easy transmission
   * @param pBuf Data to be packed
   * @param pBuf Length of data package  
   * @return sProtocol_t type, indicating return the packed data
   */
  sProtocol_t pack(uint8_t *pBuf, uint8_t pBuf);

  /**
   * @fn getSensorVoltage
   * @brief Get voltage output by sensor probe (for calculating the current gas concentration)
   * @return float type, indicating return voltage
   */
  float getSensorVoltage(void);

  /**
   * @fn dataIsAvailable
   * @brief Call this function in active mode to determine the presence of data on data line
   * @return bool type, indicating whether there is data coming from sensor
   * @retval True Has uploaded data
   * @retval False No data uploaded 
   */
  virtual bool dataIsAvailable(void) = 0;

  /**
   * @fn changeI2cAddrGroup
   * @brief Change I2C address group
   * @param group Address group select
   * @return int type, indicating return init status
   * @retval bool type
   * @retval True Change succeed
   * @retval False Change failed
   */
  bool changeI2cAddrGroup(uint8_t group);
```
## Compatibility

MCU                | Work Well | Work Wrong | Untested  | Remarks
------------------ | :----------: | :----------: | :---------: | -----
FireBeetle-ESP32  |      √       |             |            | 
FireBeetle-ESP8266|      √       |              |             | 
Mega2560  |      √       |             |            | 
Arduino uno |       √      |             |            | 
Leonardo  |      √       |              |             | 
Micro：bit  |      √       |              |             | 
M0  |      √       |              |             | 

## History

- 2021/4/2 - 2.0.0 版本

## Credits

Written by PengKaixing(kaixing.peng@dfrobot.com), 2021. (Welcome to our [website](https://www.dfrobot.com/))
