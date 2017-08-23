#!/usr/bin/python

"""
== Using Audio VU Meters to Monitor System Activity on Raspberry Pi ==

==== Dual Channel Digital to Analog Converter with custom Library ====

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

MIT License
"""

from __future__ import division

import RPi.GPIO as GPIO
from MCP4922 import MCP4922

import atexit
import time
import sys

# PS UTIL for monitoring the system activity
import psutil

import math

# Network settings, maximum bandwidth is 15 MB/s so net_max = 15,000,000 bytes
net_max = 15000000

# DAC Maximum Value, it is a 12 bit DAC, so it has 4096 steps, but we limit it to 600 only.
dac_max = 600

cpu_channel = 0
net_channel = 1

# Polling cycle, set here the amount of seconds that you want to have calculated. E.g. for 5 seconds, just enter 5
polling_max = 1

# Growth function constants
B0 = 0
k = 0.02
S = 700  # setting the limit of the growth function a bit higher, gave me best results

# GPIO Setup

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

dac = MCP4922()


def net_coeffiecient(bytes_received_after, bytes_received_before, bytes_send_after, bytes_send_before):
    """
    Here we set the current network traffic in relation to our maximum bandwidth
    in this example, we expect a maximum (net_max) of 15 MB/s
    to make this part not too complicated, the receiving traffic and sending traffic is just added together
    then divided, finally we normalize the value on a scale from 0 to 100
    """
    net_current = ((bytes_received_after - bytes_received_before) +
                   (bytes_send_after - bytes_send_before))
    x = (net_current / net_max) * 100
    #print("Current Network usage in percent is: {}" .format(x))
    if x > 100:
        return 100
    elif x < 0:
        return 0
    else:
        return x
    return x


def B(t):
    """
    This function calculates the DAC Value based on limited growth, that gives us a slight curve,
    instead of strictly linear function.
    You can adjust k and S at the top of this file
    """
    return S - (S - B0) * math.exp(-k * t)


"""
You can also make a linear function like this:
def f(x):
    return (dac_max / 100) * x

"""


def bytes2human(n):
    """
    Function for debugging, taken from PSUTIL Script collection
    >>> bytes2human(10000)
    '9.8 K'
    >>> bytes2human(100001221)
    '95.4 M'
    """
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.2f %s' % (value, s)
    return '%.2f B' % (n)


def percent2dac(n):
    """
    Calculates the DAC Value based on the percent of network / CPU usage
    if you want to change to a linear function, change here
    """
    dac_float = B(n)
    if dac_float > dac_max:
        return dac_max
    elif dac_float < 0:
        return 0
    else:
        return int(dac_float)


def poll(interval):
    """
    Function to poll the current network usage and CPU usage
    Retrieve raw stats within an interval window
    """
    net_before = psutil.net_io_counters()
    # psutil.cpu_percent() includes a sleep for 1 second (interval)
    dac_cpu = psutil.cpu_percent(interval)
    net_after = psutil.net_io_counters()
    dac_network = net_coeffiecient(
        net_after.bytes_recv, net_before.bytes_recv, net_after.bytes_sent, net_before.bytes_sent)
    return dac_network, dac_cpu


def main():
    """
    Starting by defining some variables
    main function
    """
    net_total = 0
    cpu_total = 0
    counter = 0
    try:
        interval = 0
        while True:
            net_poll, cpu_poll = poll(interval)
            net_total += net_poll
            cpu_total += cpu_poll
            # Print for debug only
            #print('Net Total: {}' .format(net_total))
            #print("CPU Total: {}" .format(cpu_total))
            interval = 1  # Poll every second
            counter += 1
            #print("Counter: {}" .format(counter))
            time.sleep(0.01)  # reduce strain on CPU
            # count to your desired period and then update the DAC for the VU meter
            if counter == polling_max:
                dac.setVoltage(net_channel, percent2dac(
                    net_total / polling_max))  # the magic happens here!
                dac.setVoltage(cpu_channel, percent2dac(
                    cpu_total / polling_max))
                counter = 0
                net_total = 0
                cpu_total = 0
                # print(counter)
                time.sleep(0.01)  # Reduce strain on CPU
    except (KeyboardInterrupt, SystemExit):
        """ Cleaning Up """
        dac.setVoltage(0, 0)
        dac.setVoltage(1, 0)
        dac.shutdown(0)
        dac.shutdown(1)
        GPIO.cleanup()
        sys.exit(0)


if __name__ == '__main__':
    main()
