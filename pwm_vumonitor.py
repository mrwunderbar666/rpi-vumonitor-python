#!/usr/bin/python

"""
== Using Audio VU Meters to Monitor System Activity on Raspberry Pi ==

==== Pulse Width Modulation and standard RPi.GPIO Library ====

In this version we use software PWM to pulse the VU Meters.
I noticed that this method creates a lot of jitter and is quite inaccurate.
Also the resolution is quite low, as my VU Meters already are at maximum
level with a PWM Duty Cycle of 10 @200 Hz.

But this is also the most simple and straightforward method.

Requires:

- RPi.GPIO
- psutil (monitoring system)

MIT License
"""

from __future__ import division

import RPi.GPIO as GPIO

import atexit
import time
import sys

# PS UTIL for monitoring the system activity
import psutil

import math

# Network settings, maximum bandwidth is 15 MB/s so net_max = 15,000,000 bytes
net_max = 15000000

# Experiment with these values:
pwm_max = 10  # PWM Maximum Duty Cycle
pwm_freq = 200  # 200 Hz frequency seems like a good value here

# GPIO Pins
vu_pin_cpu = 23  # BCM23, Physical 16
vu_pin_network = 24  # BCM24, Physical 18

# Polling cycle, set here the amount of seconds that you want to have calculated. E.g. for 5 seconds, just enter 5
polling_max = 1

# Growth function constants
B0 = 0
k = 0.02


# GPIO Setup

GPIO.setmode(GPIO.BCM)

GPIO.setup(vu_pin_cpu, GPIO.OUT)
GPIO.setup(vu_pin_network, GPIO.OUT)

pcpu = GPIO.PWM(vu_pin_cpu, pwm_freq)
pnet = GPIO.PWM(vu_pin_network, pwm_freq)


def net_coeffiecient(bytes_received_after, bytes_received_before, bytes_send_after, bytes_send_before):
    net_current = ((bytes_received_after - bytes_received_before) +
                   (bytes_send_after - bytes_send_before))
    """
    Here we set the current network traffic in relation to our maximum bandwidth
    in this example, we expect a maximum (net_max) of 15 MB/s
    to make this part not too complicated, the receiving traffic and sending traffic is just added together
    then divided, finally we normalize the value on a scale from 0 to 100
    """
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
    This function calculates the PWM Duty cycle based on limited growth, that gives us a slight curve,
    instead of strictly linear function.
    You can adjust k and pwm_max at the top of this file
    """
    return pwm_max - (pwm_max - B0) * math.exp(-k * t)


"""
You can also make a linear function like this:
def f(x):
    return (pwm_max / 100) * x

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


def percent2pwm(n):
    """
    Calculates the duty cycle for PWM based on the percent of network / CPU usage
    if you want to change to a linear function, change here
    """
    pwm_float = B(n)
    if pwm_float > pwm_max:
        return pwm_max
    elif pwm_float < 0:
        return 0
    else:
        return pwm_float


def poll(interval):
    """
    Function to poll the current network usage and CPU usage
    Retrieve raw stats within an interval window.
    """
    net_before = psutil.net_io_counters()
    # psutil.cpu_percent() includes a sleep for 1 second (interval)
    pwm_cpu = psutil.cpu_percent(interval)
    net_after = psutil.net_io_counters()
    pwm_network = net_coeffiecient(
        net_after.bytes_recv, net_before.bytes_recv, net_after.bytes_sent, net_before.bytes_sent)
    return pwm_network, pwm_cpu


def main():
    """
    main function
    Starting by defining some variables
    """
    net_total = 0
    cpu_total = 0
    counter = 0
    try:
        # Start PWM
        pnet.start(0)
        pcpu.start(0)
        # first polling interval is 0
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
            time.sleep(0.01)  # small sleep to reduce strain on CPU
            # count to your desired period and then update the PWM for the VU meter
            if counter == polling_max:
                # the magic happens here!
                pnet.ChangeDutyCycle(percent2pwm(net_total / polling_max))
                pcpu.ChangeDutyCycle(percent2pwm(cpu_total / polling_max))
                counter = 0
                net_total = 0
                cpu_total = 0
                # print(counter)
            time.sleep(0.01)

    except (KeyboardInterrupt, SystemExit):
        """ Good habit to clean up after yourself """
        pnet.stop()
        pcpu.stop()
        GPIO.cleanup()
        pass


if __name__ == '__main__':
    main()
