# Description
_Using Audio VU Meters to visualize CPU and Network usage of your Raspberry Pi._

A collection of python scripts that enable different methods of driving analog VU Meters from your Raspberry Pi GPIOs

## [Project on Hackaday.io](https://hackaday.io/project/26951-audio-vu-meters-raspberry-pi)

## [Documentation on GitHub](https://github.com/mrwunderbar666/rpi-vumonitor-python/blob/master/docs/index.md)

# Requirements

- RPI.GPIO
- psutil
- Wiring Pi
- MCP4922 Driver
- MCP4725 Driver

# 4 Different Methods



## Pulse Width Modulation and standard RPi.GPIO Library
_Software PWM_

In this version we use software PWM to pulse the VU Meters.
I noticed that this method creates a lot of jitter and is quite inaccurate.
Also the resolution is quite low, as my VU Meters already are at maximum
level with a PWM Duty Cycle of 10 @ 200 Hz.

But this is also the most simple and straightforward method.

### Requires:

- RPi.GPIO
- psutil (monitoring system)

## Pulse Width Modulation and WiringPi GPIO Library
_Hardware PWM_

In this version we use hardware PWM to pulse the VU Meters.
The wiringpi library supports hardware PWM, unlike the RPi.GPIO library.

This method has only little jitter and is more accurate compared to the
software PWM version.
Resolution is also better compared to the software PWM. I can get around
200 steps of duty cycle until the VU Meter is at its peak.


### Requires:

- Wiring Pi
- psutil (monitoring system)

## Dual Channel Digital to Analog Converter with custom Library
_Using MCP4922 DAC_

In this version we use an MCP4922 DAC to apply a constant voltage to two
VU Meters.
The MCP4922 is a Digital to Analog Converter with 2 Channels and 12 bit
resolution.

It supports SPI, which is a bit painful to use at the beginning.

This method is very clean, has no jitter and highly accurate.
The resolution is effectively at around 600 steps, because the DAC can
adjust the voltage in 1mV steps.

I opted for this as my permanent solution

Requires:

- RPi.GPIO
- MCP4922 Driver (https://github.com/mrwunderbar666/Python-RPi-MCP4922)
- psutil (monitoring system)

## Single Channel Digital to Analog Converter with Adafruit Library
_Using MCP4725 DAC_

In this version we use an MCP4725 DAC to apply a constant voltage to one
VU Meter.
The MCP4725 is a Digital to Analog Converter with 1 Channel and 12 bit
resolution. It supports I2C, which is nice and easy to use.

Adafruit offers a breakout version and supplies some libraries for it.

This method is very clean, has no jitter and highly accurate.
The resolution is effectively at around 600 steps, because the DAC can
adjust the voltage in 1mV steps.

But has only one channel. So it is not a good solution if you want to drive
several VU Meters at once.
Requires:

- MCP4725 Library (https://github.com/adafruit/Adafruit_Python_MCP4725)
- psutil (monitoring system)
