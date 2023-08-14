# DFRobot_MultiGasSensor
- [English Version](./README.md)

气体传感器广泛应用在气体研究，环境检测，生产安全监测，溶解气体分析，污染源/排放口规律研究，有毒有害，可燃气体检测报警，化验室或现场简单气体分析测试等方面，这款气体传感器更是集成了多种气体探头的一个多气体传感器，可以适用于各种各样的应用场景
![正反面svg效果图](../../resources/images/DFR0784.png)

## 产品链接(https://www.dfrobot.com/)

SKU：DFR0784

## 目录

* [概述](#概述)
* [库安装](#库安装)
* [方法](#方法)
* [兼容性](#兼容性y)
* [历史](#历史)
* [创作者](#创作者)

## 概述

这是一个用于复杂环境中检测多种气体的传感器，支持O2 CO H2S 
NO2 O3 CL2 NH3 H2 HCL SO2 HF PH3等气体。只需要硬件切换对应
的探头就可以了。同时支持气体高阈值或者低阈值报警功能

## 库安装

使用此库前，请首先下载库文件，将其粘贴到\Arduino\libraries目录中，然后打开examples文件夹并在该文件夹中运行演示。

## 方法

```python
  '''!
    @brief 解析传感器返回的数据
    @param recv 获取到的数据
  '''
  def analysis_all_data(self,recv):

  '''
  @brief 改变传感器采集到气体以后数据上报到主控的方式
  @param INITIATIVE：传感器主动上报
         PASSIVITY ：主控发送请求，传感器才能上报数据
  @return status
          True is ： change success
          False is： change fail
  '''
  def change_acquire_mode(self,mode):

  '''
    @brief 获取传感器获取的气体浓度或者气体的类型
    @param gastype    ：此时的传感器的类型
         O2 ：氧气
         CO ：一氧化碳
         H2S：硫化氢
         NO2：二氧化氮
         O3 ：臭氧
         CL2：氯气
         NH3：氨气
         H2 ：氢气
         HF ：氟化氢
         PH3：磷化氢
    @return 如果数据传输正常，那么返回气体浓度
      否则，返回0xffff
  '''
  def read_gas_concentration(self):

  '''
    @brief 改变传感器采集到气体以后数据上报到主控的方式
    @param INITIATIVE：传感器主动上报
         PASSIVITY ：主控发送请求，传感器才能上报数据
    @return status
          True is ： change success
          False is： change fail
  '''
  def change_acquire_mode(self,mode):

  '''
    @brief 获取传感器获取的气体浓度或者气体的类型
    @param gastype    ：此时的传感器的类型
         O2 ：氧气
         CO ：一氧化碳
         H2S：硫化氢
         NO2：二氧化氮
         O3 ：臭氧
         CL2：氯气
         NH3：氨气
         H2 ：氢气
         HF ：氟化氢
         PH3：磷化氢
    @return 如果数据传输正常，那么返回气体浓度
      否则，返回0xffff
  '''
  def read_gas_concentration(self):      

  '''
    @brief 获取传感器获取气体的类型
    @param 无
    @return 气体类型
        O2   0x05
        CO   0x04
        H2S  0x03
        NO2  0x2C
        O3   0x2A
        CL2  0x31
        NH3  0x02
        H2   0x06
        HCL  0X2E
        SO2  0X2B
        HF   0x33
        PH3  0x45
  '''
  def read_gas_type(self):  

  '''
    @brief 设置传感器报警的阈值
    @param switchof    ：设置是否打开报警
           ON          ：打开报警功能
           OFF         ：关闭报警功能
           threshold   ：设置报警的阈值
           returntype ：
           GASCON     :气体浓度
    @return status  ： init status
            True is ： init success
            False is： init error
  '''
  def set_threshold_alarm(self,switchof,threshold):    

  '''
    @brief 获取传感器的板载温度
    @param 无
    @return 以float类型返回当前板子的温度
  '''
  def read_temp(self):    

  '''
    @brief 设置是否开启温度补偿，传感器在不同温度下的输出值会有差别，所以
          为了获取到的气体浓度更精确，在计算气体浓度的时候需要增加温度补偿
    @param tempswitch：
          ON          ：打开温度补偿
          OFF         ：关闭温度补偿
    @return 无
  '''
  def set_temp_compensation(self,tempswitch):      

  '''
    @brief 设置是否开启温度补偿，传感器在不同温度下的输出值会有差别，所以
          为了获取到的气体浓度更精确，在计算气体浓度的时候需要增加温度补偿
    @param tempswitch：
          ON          ：打开温度补偿
          OFF         ：关闭温度补偿
    @return 无
  '''
  def set_temp_compensation(self,tempswitch):

  '''
    @brief 获取传感器气体浓度以原始电压输出，不同于直接读取传感器寄存器，这
          个函数主要用来检验读取的气体浓度是否准确
    @param  vopin：用来接收传感器探头原始电压输出的引脚
    @return 传感器气体浓度的原始电压输出
  '''
  def read_volatage_data(self):          
```

## 兼容性

| 主板         | 通过 | 未通过 | 未测试 | 备注 |
| ------------ | :--: | :----: | :----: | :--: |
| RaspberryPi2 |      |        |   √    |      |
| RaspberryPi3 |      |        |   √    |      |
| RaspberryPi4 |  √   |        |        |      |

* Python 版本

| Python  | 通过 | 未通过 | 未测试 | 备注 |
| ------- | :--: | :----: | :----: | ---- |
| Python2 |  √   |        |        |      |
| Python3 |  √   |        |        |      |

## 历史

- 2021/4/2 - 2.0.0 版本

## 创作者

Written by PengKaixing(kaixing.peng@dfrobot.com), 2021. (Welcome to our [website](https://www.dfrobot.com/))