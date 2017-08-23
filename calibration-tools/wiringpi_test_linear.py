#!/usr/bin/python

"""
== VU Meter Calibration Toolkit ==

==== Pulse Width Modulation and WiringPi GPIO Library ====

Hardware PWM

Loop trough the min and max value
uses linear function


Requires:

- Wiring Pi

MIT License
"""

from __future__ import division

import wiringpi

import time
import math


# PWM Maximum Duty Cycle
S = 200

# math stuff
# Growth function constants
B0 = 0

""" Configure your pin here """
PIN_TO_PWM = 18  # Physical Pin 12
OUTPUT = 2

wiringpi.wiringPiSetupGpio()

# Linear function
def B(t):
    return (S / 100) * t


try:
    wiringpi.pinMode(PIN_TO_PWM, OUTPUT)
    wiringpi.pwmWrite(PIN_TO_PWM, 0)  # Setup PWM using Pin, Initial Value
        while True:
            for i in range(100):
                pwm_float = B(i)
                wiringpi.pwmWrite(PIN_TO_PWM, int(pwm_float))
                print("i = {}, pwm_float = {}" .format(i, pwm_float))
                time.sleep(0.1)
            for i in range(100):
                pwm_float = B(i)
                wiringpi.pwmWrite(PIN_TO_PWM, int(pwm_float))
                print("i = {}, pwm_float = {}" .format(i, pwm_float))
                time.sleep(0.1)

except KeyboardInterrupt:
    # manual cleanup
    wiringpi.pwmWrite(PIN_TO_PWM, 0)
    wiringpi.pinMode(PIN_TO_PWM, 0)
    pass
