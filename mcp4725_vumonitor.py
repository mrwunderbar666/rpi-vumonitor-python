#!/usr/bin/python

"""
== Using Audio VU Meters to Monitor System Activity on Raspberry Pi ==

==== Single Channel Digital to Analog Converter with Adafruit Library ====

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

MIT License
"""

from __future__ import division

# DAC Library
import Adafruit_MCP4725

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

# Polling cycle, set here the amount of seconds that you want to have calculated. E.g. for 5 seconds, just enter 5
polling_max = 1

# Growth function constants
B0 = 0
k = 0.02
S = 700 #setting the limit of the growth function a bit higher, gave me best results

# DAC Setup

dac = Adafruit_MCP4725.MCP4725()

def net_coeffiecient(bytes_received_after, bytes_received_before, bytes_send_after, bytes_send_before):
    """
    Here we set the current network traffic in relation to our maximum bandwidth
    in this example, we expect a maximum (net_max) of 15 MB/s
    to make this part not too complicated, the receiving traffic and sending traffic is just added together
    then divided, finally we normalize the value on a scale from 0 to 100
    """
    net_current = ((bytes_received_after - bytes_received_before) + ( bytes_send_after - bytes_send_before))
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
    return S - (S - B0)*math.exp(-k*t)


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
    dac_network = net_coeffiecient(net_after.bytes_recv, net_before.bytes_recv, net_after.bytes_sent, net_before.bytes_sent)
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
            interval = 1 # Poll every second
            counter += 1
            #print("Counter: {}" .format(counter))
            # count to your desired period and then update the DAC for the VU meter
            if counter == polling_max:
                """ Because the MCP 4725 has only one channel, you can choose here """
                dac.set_voltage(percent2dac(net_total / polling_max))  # Display Network Usage
                # dac.set_voltage(percent2dac(cpu_total / polling_max)) # Display CPU Usage
                counter = 0
                net_total = 0
                cpu_total = 0
    except (KeyboardInterrupt, SystemExit):
        """ Cleaning Up """
        dac.set_voltage(0)
        sys.exit(0)

if __name__ == '__main__':
    main()
