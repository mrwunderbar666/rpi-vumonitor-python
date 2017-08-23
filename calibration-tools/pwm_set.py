#!/usr/bin/python

"""
== VU Meter Calibration Toolkit ==

==== Pulse Width Modulation and standard RPi.GPIO Library ====

Software PWM

Manually set the PWM Value and calibrate your output!


Requires:

- Wiring Pi

MIT License
"""
from __future__ import division

import RPi.GPIO as GPIO

import time

# Select you PWM Pin
PIN_TO_PWM = 23  # BCM23, Physical 16
frequency = 200  # we use 200 Hz here, that gave nice results

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
