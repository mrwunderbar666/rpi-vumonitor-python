#!/usr/bin/python

"""
== VU Meter Calibration Toolkit ==

==== Pulse Width Modulation and WiringPi GPIO Library ====

Hardware PWM

Manually set the PWM Value and calibrate your output!

Requires:

- Wiring Pi

MIT License
"""

from __future__ import division

import wiringpi

import time

""" Configure your pin here """
PIN_TO_PWM = 18  # Physical Pin 12
OUTPUT = 2

wiringpi.wiringPiSetupGpio()

wiringpi.pinMode(PIN_TO_PWM, OUTPUT)
wiringpi.pwmWrite(PIN_TO_PWM, 0)  # Setup PWM using Pin, Initial Value

print("Press CTRL + C to exit")

try:
    while True:
        pwm_value = int(raw_input("Select PWM Value: "))
        wiringpi.pwmWrite(PIN_TO_PWM, pwm_value)

except KeyboardInterrupt:
    # manual cleanup
    wiringpi.pwmWrite(PIN_TO_PWM, 0)
    wiringpi.pinMode(PIN_TO_PWM, 0)
    pass
