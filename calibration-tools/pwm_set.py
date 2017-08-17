#!/usr/bin/python

"""
== VU Meter Calibration Toolkit ==

==== Pulse Width Modulation and standard RPi.GPIO Library ====

Software PWM

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

import RPi.GPIO as GPIO

import time

PIN_TO_PWM = 13 # Select you PWM Pin
frequency = 200 # we use 200 Hz here, that gave nice results

GPIO.setmode(GPIO.BCM)

GPIO.setup(PIN_TO_PWM, GPIO.OUT) 
p = GPIO.PWM(PIN_TO_PWM, frequency)        

p.start(0)
print("Press CTRL + C to exit")

try:
        while True:
                pwm_value = float(raw_input("Select Value: "))
                p.ChangeDutyCycle(pwm_value)

except KeyboardInterrupt:
        # Cleanup
        p.stop()
        GPIO.cleanup()
        pass


