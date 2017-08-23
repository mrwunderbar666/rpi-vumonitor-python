#!/usr/bin/python
"""
== VU Meter Calibration Toolkit ==

=== MCP4922 DAC ===

Incrementally increases and decreases voltage from 0 to 600
never ending loop on both channels

MIT License
"""

import time
import sys
import RPi.GPIO as GPIO

from MCP4922 import MCP4922

GPIO.setmode(GPIO.BCM)                 # use the Broadcom pin numbering
GPIO.setwarnings(False)             # disable warnings


if __name__ == '__main__':
    dac = MCP4922()
    try:
        while True:
            x = 0
            for i in range(0, 100):
                x = x + 6
                dac.setVoltage(0, x)
                dac.setVoltage(1, x)
                print(x)
                time.sleep(0.1)
            for i in range(0, 100):
                x = x - 6
                dac.setVoltage(0, x)
                dac.setVoltage(1, x)
                print(x)
                time.sleep(0.1)

    except KeyboardInterrupt:   # Press CTRL C to exit program
        dac.setVoltage(0, 0)
        dac.setVoltage(1, 0)
        dac.shutdown(0)
        dac.shutdown(1)
        GPIO.cleanup()
        sys.exit(0)
