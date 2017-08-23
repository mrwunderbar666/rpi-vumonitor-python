#!/usr/bin/python

"""
== VU Meter Calibration Toolkit ==

==== Pulse Width Modulation and standard RPi.GPIO Library ====

Software PWM
Loop trough the min and max value
uses linear function


Requires:

- RPi.GPIO

MIT License
"""

from __future__ import division

import RPi.GPIO as GPIO

import time
import math

# PWM Maximum Duty Cycle
S = 10
# we use 200 Hz here, that gave nice results
pwm_freq = 200

""" Configure your pins here """
vu_pin1 = 23  # BCM23 Physical 16
vu_pin2 = 24  # BCM24 Physical 18

# math stuff
# Growth function constants
B0 = 0

# GPIO Setup
GPIO.setmode(GPIO.BCM)

GPIO.setup(vu_pin1, GPIO.OUT)
GPIO.setup(vu_pin2, GPIO.OUT)

p1 = GPIO.PWM(vu_pin1, pwm_freq)
p2 = GPIO.PWM(vu_pin2, pwm_freq)

# Linear function


def B(t):
    return (S / 100) * t


try:
    # start PWM
    p1.start(0)
    p2.start(0)
        while True:
            for i in range(100):
                pwm_float = B(i)
                p1.ChangeDutyCycle(pwm_float)
                p2.ChangeDutyCycle(pwm_float)
                print("i = {}, pwm_float = {}" .format(i, pwm_float))
                time.sleep(0.1)
            for i in range(100):
                pwm_float = B(i)
                p1.ChangeDutyCycle(S - pwm_float)
                p2.ChangeDutyCycle(S - pwm_float)
                print("i = {}, pwm_float = {}" .format(i, pwm_float))
                time.sleep(0.1)

except KeyboardInterrupt:
        # Cleanup
    p1.stop()
    p2.stop()
    GPIO.cleanup()
    pass
