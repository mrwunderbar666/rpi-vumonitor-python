#!/usr/bin/python

"""
== VU Meter Calibration Toolkit ==

==== Pulse Width Modulation and WiringPi GPIO Library ====

Hardware PWM

Manually set the PWM Value and calibrate your output!


Requires:

- Wiring Pi
- psutil (monitoring system)

MIT License
Copyright (c) 2017 mrwunderbar666
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import division

import wiringpi

import time

""" Configure your pin here """
PIN_TO_PWM = 18
OUTPUT = 2

wiringpi.wiringPiSetupGpio()

wiringpi.pinMode(PIN_TO_PWM,OUTPUT)
wiringpi.pwmWrite(PIN_TO_PWM,0) # Setup PWM using Pin, Initial Value

print("Press CTRL + C to exit")

try:
        while True:
                pwm_value = int(raw_input("Select PWM Value: "))
                wiringpi.pwmWrite(PIN_TO_PWM,pwm_value)

except KeyboardInterrupt:
        # manual cleanup
        wiringpi.pwmWrite(PIN_TO_PWM, 0)
        wiringpi.pinMode(PIN_TO_PWM, 0)
        pass

