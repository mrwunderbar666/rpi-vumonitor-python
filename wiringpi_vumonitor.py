#!/usr/bin/python

"""
== Using Audio VU Meters to Monitor System Activity on Raspberry Pi ==

==== Pulse Width Modulation and WiringPi GPIO Library ====

In this version we use hardware PWM to pulse the VU Meters.
The wiringpi library supports hardware PWM, unlike the RPi.GPIO library.

This method has only little jitter and is more accurate compared to the
software PWM version.
Resolution is also better compared to the software PWM. I can get around
200 steps of duty cycle until the VU Meter is at its peak.


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

import atexit
import time
import sys

# PS UTIL for monitoring the system activity
import psutil

import math

# Network settings, maximum bandwidth is 15 MB so net_max = 15,000,000 bytes
net_max = 15000000

# Experiment with these values: 
pwm_max = 200 # PWM Maximum Duty Cycle

# Only specific Pins support hardware PWM
vu_pin_cpu = 18 #BCM18 Physical 12
vu_pin_network = 13 #BCM13 Physical 33

# Polling cycle, set here the amount of seconds that you want to have calculated. E.g. for 5 seconds, just enter 5
polling_max = 1

# Growth function constants
B0 = 0
k = 0.02

# GPIO Setup

wiringpi.wiringPiSetupGpio()

wiringpi.pinMode(vu_pin_cpu, 2) # output mode 2 is hardware PWM
wiringpi.pwmWrite(vu_pin_cpu, 0) # Setup PWM using Pin, Initial Value

wiringpi.pinMode(vu_pin_network, 2)
wiringpi.pwmWrite(vu_pin_network, 0)


# Here we set the current network traffic in relation to our maximum bandwidth
# in this example, we expect a maximum (net_max) of 15 MB/s 
# to make this part not too complicated, the receiving traffic and sending traffic is just added together
# then divided, finally we normalize the value on a scale from 0 to 100

def net_coeffiecient(bytes_received_after, bytes_received_before, bytes_send_after, bytes_send_before):
    net_current = ((bytes_received_after - bytes_received_before) + ( bytes_send_after - bytes_send_before))
    #print (net_current)
    x = (net_current / net_max) * 100
    #print("Current Network usage in percent is: {}" .format(x))
    if x > 100:
        return 100
    elif x < 0:
        return 0
    else:
        return x
    return x

# This function calculates the PWM Duty cycle based on limited growth, that gives us a slight curve,
# instead of strictly linear function.
# You can adjust k and pwm_max at the top of this file 

def B(t):
    return pwm_max - (pwm_max - B0)*math.exp(-k*t)


#You can also make a linear function like this:
"""
def f(x):
    return (pwm_max / 100) * x

"""

# Function for debugging, taken from PSUTIL Script collection

def bytes2human(n):
    """
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


# Calculates the duty cycle for PWM based on the percent of network / CPU usage
def percent2pwm(n):
    pwm_float = B(n)
    if pwm_float > pwm_max:
        return pwm_max
    elif pwm_float < 0:
        return 0
    else:
        return pwm_float


# Function to poll the current network usage and CPU usage
def poll(interval):
    """Retrieve raw stats within an interval window."""
    net_before = psutil.net_io_counters()    
    # psutil.cpu_percent() includes a sleep for 1 second (interval)
    pwm_cpu = psutil.cpu_percent(interval)
    net_after = psutil.net_io_counters()    
    pwm_network = net_coeffiecient(net_after.bytes_recv, net_before.bytes_recv, net_after.bytes_sent, net_before.bytes_sent)
    return pwm_network, pwm_cpu

# main function
def main():
    """ Starting by defining some variables """
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
            time.sleep(0.01) #small sleep to reduce strain on CPU            
            # count to your desired period and then update the PWM for the VU meter
            if counter == polling_max:
                wiringpi.pwmWrite(vu_pin_cpu, int(percent2pwm(cpu_total / polling_max)))  # the magic happens here!
                wiringpi.pwmWrite(vu_pin_network, int(percent2pwm(net_total / polling_max))) 
                counter = 0
                net_total = 0
                cpu_total = 0
                #print(counter)
            time.sleep(0.01)

    except (KeyboardInterrupt, SystemExit):
        # manual cleanup
        wiringpi.pwmWrite(vu_pin_cpu, 0)
        wiringpi.pwmWrite(vu_pin_network, 0)
        wiringpi.pinMode(vu_pin_cpu, 0)
        wiringpi.pinMode(vu_pin_network, 0)
        pass

if __name__ == '__main__':
    main()
