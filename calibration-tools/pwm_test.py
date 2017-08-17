#!/usr/bin/python

"""
== VU Meter Calibration Toolkit ==

==== Pulse Width Modulation and standard RPi.GPIO Library ====

Software PWM
Loop trough the min and max value
uses limited growth function, instead of linear function


Requires:

- RPi.GPIO
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
import math

## math stuff

# PWM Maximum Duty Cycle
S = 10
pwm_freq = 200

""" Configure your pins here """
vu_pin1 = 23 #BCM23 Physical 12
vu_pin2 = 24 #BCM24 Physical 13

# Growth function constants
B0 = 0
k = 0.02

# GPIO Setup
GPIO.setmode(GPIO.BCM)

GPIO.setup(vu_pin1, GPIO.OUT)
GPIO.setup(vu_pin2, GPIO.OUT)

p1 = GPIO.PWM(vu_pin1,pwm_freq)        # we use 200 Hz here, that gave nice results
p2 = GPIO.PWM(vu_pin2,pwm_freq)        # we use 200 Hz here, that gave nice results

# start PWM
p1.start(0)
p2.start(0)

# Growth function, because I love math :P
def B(t):
    return S - (S - B0)*math.exp(-k*t)

try:
        while True:
                for i in range (100):
                        pwm_float = B(i)
                        p1.ChangeDutyCycle(pwm_float)
                        p2.ChangeDutyCycle(pwm_float)
                        print("i = {}, pwm_float = {}" .format(i, pwm_float))
                        time.sleep(0.1)
                for i in range(100):
                        pwm_float = B(i)
                        p1.ChangeDutyCycle(S-pwm_float)
                        p2.ChangeDutyCycle(S-pwm_float)
                        print("i = {}, pwm_float = {}" .format(i, pwm_float))
                        time.sleep(0.1)

except KeyboardInterrupt:
        # Cleanup
        p1.stop()
        p2.stop()
        GPIO.cleanup()
        pass

