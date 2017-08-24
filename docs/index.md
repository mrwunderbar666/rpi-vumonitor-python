# Description
_Using Audio VU Meters to visualize CPU and Network usage of your Raspberry Pi._

## Result
_Click to watch_

[![Click to watch](https://github.com/mrwunderbar666/rpi-vumonitor-python/raw/master/docs/dac_speedtest.gif)](https://vid.me/Wm7bx)


Webinterfaces to monitor your RPi are neat and useful, but what if you want to have an analog display that physically shows you what your RPi is doing? 

There are many explanations out there that show how to use a small LCD Display to monitor your Raspberry Pi, but I haven't found any about using a VU meter.

This project is especially useful for people who salvage old HiFi equipment to create a casing for a Raspberry Pi. Use the old fashioned VU meters to give your raspberry pi a more hipster look :)

This is a beginner friendly tutorial and it touches on very different topics.

# Components & Tools
- Raspberry Pi 3 Model B+
- 2 VU Meter

    Any analog VU Meter will do. _Technically you can also use a voltmeter that is rated for 0 - 5V_
- Trimpots

    You should be able to adjust resistance between 0 and 20k Ohms. Maybe use more trimpots to get a finer adjustment range
- Multimeter
- Bench Power Supply

    ideally can support low voltages of less than 3 V. Best: can step up in 10mv increments
- Wires. You always need wires

## Optional Components

- MCP4299 DAC

    2 Channel, 12 bit, Digital to Analog Converter
- MCP4725 DAC

    1 Channel, 12 bit, Digital to Analog Converter
- Capacitors

    10µF and 100nF Capacitors

# Overview
So you want to use some VU Meters to display your Raspberry Pi system statistics? 

With this tutorial you can extract any system stat and have it physically represented by a VU Meter. 

This tutorial focuses on Network Bandwidth usage and CPU usage. But with a few altered lines of code you can also display: e.g. Disk write/read stats, CPU temperature, etc.

This tutorial is in several parts:

1. Understanding the VU Meter and its electrical characteristics
1. Hooking it up to the RPi
1. Using PWM (Pulse Width Modulation) to make the VU Meter Move
1. Using a DAC to make the VU Meter move
1. Accessing system statistics in Python and feed it to the VU Meter

We get started by understanding and gauging the hardware...

# Steps
## 1: Analyze your VU Meters
Firstly, we need to find out the range, sensitivity and specifications of our VU Meters. Those can vary greatly, depending on the manufacturer, type and previously intended usage.

A VU Meter is basically a low current ammeter. For this application we will focus on the voltage required to gain a specific current flow through the VU Meter. Remember that Ohm's Law states that the Current is depending on the voltage and the resistance of the circuit. You can read all details about [VU Meters on Wikipedia.](https://en.wikipedia.org/wiki/VU_meter)

VU Meters operate in a quite low voltage of around 100 - 1000 mV. Therefore, the better your bench power supply, the easier it gets.

### Let's get some basic measurements:

1. Measure your VU Meter's internal resistance using a multimeter. My VU meter has an internal resistance of 655 Ω
1. Attach DuPont Wires to your VU Meter

    I directly soldered female DuPont Wires to my meters
1. Connect your VU Meter to your bench power supply and have at least 3 trimpots in series, but do not switch on your power supply yet. My bench power supply lowest reliable voltage is 1.24 V. If your's can go lower, it is even better.
1. Set your trimpots to the highest resistance
1. Attach your multimeter to the positive and negative terminals of your VU Meter
1. Switch on your power supply
1. Slowly decrease the resistance of your trimpots until your VU Meter shows maximum deflection (needle goes towards the maximum value). 
1. Measure the voltage across the VU Meter. In my case: 0.443 V or 443 mV
1. Measure the resistance across all your trimpots. In my case: 1190 Ω

#### VU Meter Gauging Circuit
![Schematic 1: VU Meter Gauging Circuit](https://github.com/mrwunderbar666/rpi-vumonitor-python/raw/master/docs/measure-VU-Meter_schem.png)

### Calculations for the Geeks (Optional)

Now that we have some basic specifications of the VU Meter, we can make some calculations.

The current required for the needle to move is calculated using Ohm's Law:

          V
    I  =  -
          R
          
![Ohms Law](https://github.com/mrwunderbar666/rpi-vumonitor-python/raw/master/docs/formulas/ohmslaw.png)

Where I is the current, V is the voltage, and R is the resistance:

    \frac{V_{PowerSupply}}{R_{Meter}+R_{Trimpot}} = \frac{1.24 V}{659 \Omega + 1190 \Omega} = 670 \mu A

This is useful to know if you have a different Voltage value from your power supply.

#### Using a 5 V Power Supply

Let's assume you have a 5 V power supply and want to get a ballpark estimation of the required resistance of your trimpots:

    R_{Trimpot} + R_{Meter} = \frac{V}{I}
    
    R_{Trimpot} = \frac{V}{I} - R_{Meter}

Therefore we can estimate:

    \frac{5 V}{670 \mu A} - 659 \Omega = 7455 \Omega - 569 \Omega = 6796 \Omega

That you need an resistance of about **7000 Ohms** in order to drive your VU Meter properly with a 5V power supply.

## 2: Considerations for driving the VU Meter by the Raspberry Pi

Now that we understand the VU Meters, let's have a look at how to connect and drive them from the Raspberry Pi.

By default the RPi has a 3.3 V or 5 V supply rail. That would be total overkill for the sensitive VU Meters. A regular GPIO Pin delivers 3.3 V if it is set to "HIGH", so that would be also too much and not variable.

So let's have a look at how we can get that 3.3 V to a much lower value and also change the output value:

### PWM (Pulse Width Modulation)

The simplest way to control the voltage (and effective current) applied to the VU Meter is by using PWM (Pulse Width Modulation).

There are two ways of creating a PWM Signal from the RPI:

1. Software PWM (fast & simple, can use almost any GPIO)
2. Hardware PWM (special python module, can use limited GPIOs)

In the steps below, I will go into detail for both ways.

### DAC (Digital to Analog Converter)

The RPi doesn't have any DAC integrated, so we need to hook one up. 

I will go into different DACs at a later point. E.g. how many VU Meters we want to control is another consideration for choosing a DAC.

## 3: Pulse Width Modulation (PWM)

With help of the RPi.GPIO Library we can set the **frequency** and **duty cycle** for the pulses.

#### Frequency
Theoretically, the frequency should have no impact on the effective voltage applied through PWM. But after some experimentation I found that **200 Hz** is a good frequency for driving a VU Meter.

#### Duty Cycle
The duty cycle (_D_) dermines the effective voltage and current applied to the VU Meter. A duty cycle of 10 means that the voltage is applied 10% of the time. 100 equals 100% (duh!), so full voltage, and 0 equals 0% therefore 0 V.

Using a small formula:

    V_{Effective} = V_{Total} \cdot D
    
or:

    D = \frac{V_{Effective}}{V_{Total}}
    
We know that we want to get a maximum voltage of 0.443 V from a 3.3 V source. Therefore, we can calculate:

    \frac{0.443 V}{3.3 V} = 0.134 = 13.4 %

### Software PWM

#### Wiring
Very simple and easy to hook up the VU Meter to the RPi:

1. Connect the positive end of the VU Meter to GPIO Pin 23 (Physical Pin 16)
1. Connect the negative end to a GND Pin

#### Code
You can check out the [calibration tool in my github](https://github.com/mrwunderbar666/rpi-vumonitor-python/blob/master/calibration-tools/pwm_set.py) that let's you enter a duty cycle value and it will pulse the VU Meter at 200 Hz.

A small example in Python:

```python
import RPi.GPIO as GPIO # Standard GPIO module
import time

vu_pin = 23 # BCM23, Physical 16
frequency = 200 # 200 Hz

GPIO.setmode(GPIO.BCM) # Using Broadcom pin numbering scheme

GPIO.setup(vu_pin, GPIO.OUT) # Setting the pin as output

# When using GPIO in python, it is generally a good practice to use try: and except:

try:
    p = GPIO.PWM(vu_pin, frequency) # Creating the PWM Object at the vu_pin with our set frequency
    p.start(0) # Starting the PWM with a duty cycle of 0
    p.ChangeDutyCycle(10) # Pulsing the VU Meter with a duty cycle of 10 %
    time.sleep(2) # Wait 2 seconds
    p.stop() # stopping the PWM
    GPIO.cleanup()
    quit()
except KeyboardInterrupt:
    # Press CTRL + C to exit
    # Cleanup
    p.stop()
    GPIO.cleanup()
    pass
```

If you execute this code, you should observe the needle of the VU-Meter to move almost to its maximum deflection (we calculated 13.4 % above for the total maximum)

We can also incrementally increase the Duty Cycle with the help of [this little script in my github](https://github.com/mrwunderbar666/rpi-vumonitor-python/blob/master/calibration-tools/pwm_test.py).

#### The result looks like this:
_Click to watch_

[![PWM Linear](https://github.com/mrwunderbar666/rpi-vumonitor-python/raw/master/docs/pwm_lin.gif)](https://vid.me/AphL2)

[![PWM Speedtest](https://github.com/mrwunderbar666/rpi-vumonitor-python/raw/master/docs/pwm_speedtest.gif)](https://vid.me/GC4Jb)

Notice how the needles jitters and jumps occasionally. I guess this is caused by the software that doesn't produce a perfectly clean frequency of 200 Hz.

Also consider that with software PWM, we have only 13 steps of control (maybe more if we use a floating PWM variable), which isn't a very high resolution.

#### Reducing Jitter

I tried to reduce the jitter caused by the software PWM by adding a [Low Pass Filter](http://www.learningaboutelectronics.com/Articles/Low-pass-filter-calculator.php), but the results were not very satisfying. It definitely requires more tweaking to get it to work properly.

### Hardware PWM

The GPIOs of the Raspberry Pi also support hardware controlled PWM. That outputs a consistent frequency and greatly reduces the jitter at the VU Meter. However, there are only a limited amount of Pins that support hardware PWM and the GPIOs have only two hardware PWM Channels. This means we can only connect up to two VU Meters via hardware PWM.

You can find [more details here](https://pinout.xyz/pinout/pin12_gpio18).

#### Wiring

1. Connect the positive end of the VU Meter to GPIO Pin 18 (Physical Pin 12)
1. Connect the negative end to a GND Pin

#### Code
For hardware PWM we have to use the [WiringPi Library](https://github.com/WiringPi/WiringPi-Python) and make some modifications to the code example above, as the WiringPi Library uses different commands.

The duty cycle range of this library is not from 0 to 100, but from **0 - 1024**. Therefore, we need to adjust the maximum PWM Value:

    13.4 % * 1024 = 137
    
Small example in Python:

```python
import wiringpi # WiringPi Library
import time

vu_pin = 18 # BCM18, Physical 12
OUTPUT = 2 # Output mode of the Pin, 2 means PWM

wiringpi.wiringPiSetupGpio() # GPIO Setup

wiringpi.pinMode(vu_pin,OUTPUT) # Assigning the VU Meter Pin

try:
    wiringpi.pwmWrite(vu_pin, 0) # Setup PWM using Pin, Initial Value of 0
    wiringpi.pwmWrite(vu_pin, 100) # Setting a duty cycle of 100 (out of 1024)
    time.sleep(2) # Wait 2 seconds
    wiringpi.pwmWrite(vu_pin, 0) # Go back to 0
    quit()
except KeyboardInterrupt:
    # Press CTRL + C to exit
    # Manual Cleanup
    wiringpi.pwmWrite(vu_pin, 0)
    wiringpi.pinMode(vu_pin, 0)
    pass
```

It should move the VU Meter needle close to its maximum deflection and then return to 0. You can also use the [wiringpi calibration tool in my github](https://github.com/mrwunderbar666/rpi-vumonitor-python/blob/master/calibration-tools/wiringpi_setpwm.py).

#### The result looks like this:
_Click to watch_

[![Wiring Pi Linear](https://github.com/mrwunderbar666/rpi-vumonitor-python/raw/master/docs/wiringpi_lin.gif)](https://vid.me/mwaSy)

[![Wiring Pi Speedtest](https://github.com/mrwunderbar666/rpi-vumonitor-python/raw/master/docs/wiringpi_speedtest.gif)](https://vid.me/57oM4)

Notice how there is almost no jitter using the hardware PWM. And now we also have up to 137 steps of control.

## 4: Digital to Analog Converter (DAC)

With PWM we face some strong limitations: if we use software PWM we can use any GPIO pin, but get a lot of jitter. If we use hardware PWM we are limited to very few pins and two channels, but get almost no jitter.

This is were the DAC comes in. It let's us control more VU Meters at a higher level of accuracy.

### Choosing a DAC

There are plenty of choices but also some considerations to make: 

We need to have low voltages between 0 - 500 mV, and the supply source provides 3.3 V. That means we need a decent resolution.

The resolution (or steps) of the DAC depends of its bit value.

The cheaper DACs provide an 8-bit resolution, which means 256 steps:

    \frac{3300mV}{256} = 12.8 mV

So with that we can control the voltage in 12.8 mV steps. A bit too low for my taste, because there is not much gained from it comparing with PWM.

At 10-bit we get 1024 steps:

    \frac{3300mV}{1024} = 3.32 mV


So with that we can control the voltage in 3.3 mV steps. Much better, but let's take this further.

At 12-bit we have 4096 steps of resolution:

    \frac{3300mV}{4096} = 0.8 mV


12-bit seems right, because it let's us control the VU Meter in around 1 mV steps. Which provides a quite accurate signal with about 500 steps for the needle at the end.

DACs also have a varying amount of channels. So the amount of channels depend on the amount of VU Meters you want to drive. And 12-bit DACs get significantly more expensive by increasing amount of channels.

You also want to make sure that the DAC uses either SPI or I2C to communicate with the RPi via GPIOs. 

Another consideration is the packaging: there are amazing microchips out there that can do cool stuff, but some of them are only available in a Surface Mount packaging which requires a particular set of tools and skills to handle. Therefore, I prefer to get nice big DIP or through hole components that are easy to wire up.

The [MCP4725](http://ww1.microchip.com/downloads/en/DeviceDoc/22039d.pdf) is a well supported DAC with [I2C](https://en.wikipedia.org/wiki/I%C2%B2C) that is often sold with a [breakout board](http://lmgtfy.com/?q=mcp4725+breakout+board) and is therefore convenient to use. But it has only 1 channel, so you will be limited to drive only a single VU Meter from it.

After some researching I decided to go for the [MCP4922](http://ww1.microchip.com/downloads/en/DeviceDoc/22250A.pdf) which has 12-bit and two channels, and comes in a nice big DIP package. The Raspberry Pi can communicate with the chip via SPI and you can find my [python library for it here](https://github.com/mrwunderbar666/python-rpi-mcp4922). 

### Using MCP4725
If you need only one channel you can go for the MCP4725 and drive the VU Meter at good and reliable accuracy.

It supports I2C, so you need only 2 GPIO pins for communication with the device.

#### Wiring

Here is a simple wiring scheme:

    MCP4725     =>  RPi
    SCL         ->  GPIO3 (Physical 5)
    SDA         ->  GPIO2 (Physical 3)
    VDD         ->  3.3 V (Physical 1)
    VSS         ->  GND (Physical 6)
    VOUT        ->  VU Meter Positive
    
It is a good idea to add resistors to the SCL and SDA connections and also to add a bypass capacitor from the 3.3 V rail to the MCP4725. In breadboard it would look like this:

![Breadboard 2: MCP4725 Circuit](https://github.com/mrwunderbar666/rpi-vumonitor-python/raw/master/docs/mcp4725_sketch_bb.png)

And here is a schematic view of the circuit:

![Schematic 2: MCP4725 Circuit](https://github.com/mrwunderbar666/rpi-vumonitor-python/raw/master/docs/mcp4725_sketch_schem.png)

#### Code

You will have to get the correct library to drive the chip, I recommend to use the [Adafruit library here](https://github.com/adafruit/Adafruit_Python_MCP4725). You can also have a look at their [tutorial for the chip](https://learn.adafruit.com/mcp4725-12-bit-dac-with-raspberry-pi/overview), if you need more information.

Following the logic of the previous code examples, we can test the DAC and the VU Meter like this:

```python
import Adafruit_MCP4725 # Adafruit DAC Library
import time

# DAC Setup
dac = Adafruit_MCP4725.MCP4725()

try:
    dac.set_voltage(0) # Setting a starting voltage of 0
    dac.set_voltage(500) # Setting a Voltage value of 500, equals 402 mV
    time.sleep(2) # Wait 2 seconds
    dac.set_voltage(0) # Go back to 0
    quit()
except KeyboardInterrupt:
    # Press CTRL + C to exit
    # Cleanup
    dac.set_voltage(0)
    sys.exit(0)
    pass

```

And as before, this should move the needle close to the maximum deflection and back. 

### Using MCP4922

This is my go to solution, because of the reasons mentioned above. Please note that the MCP4922 supports SPI interface only, so we'll need three wires to control the chip. 

#### Wiring

    MCP4922    =>   Raspberry Pi
    CS         ->   GPIO08 Physical Pin 24 (SPI0 CE0) => Can be changed
    SDI        ->   GPIO10 Physical Pin 19 (SPI0 MOSI) => cannot be changed in hardware SPI MODE
    SCK        ->   GPIO11 Physical Pin 23 (SPI0 SCLK) => cannot be changed in hardware SPI MODE
    LDAC       ->   GND
    SHDN       ->   3.3 V
    V Ref A    ->   3.3 V
    V Ref B    ->   3.3 V
    VSS        ->   GND
    
    MCP4922    =>   VU Meters
    V Out A    ->   VU Meter 1
    V Out B    ->   VU Meter 2
    
For this ciruit it is also a good idea to add two bypass capacitors. The circuit get's slightly more complex:

![Breadboard 3: MCP4922 Breadboard Circuit](https://github.com/mrwunderbar666/Python-RPi-MCP4922/raw/master/documentation/mcp4922sketch_bb.png)

And the schematic view:

![Schematic 3: MCP4922 Schematic Circuit](https://github.com/mrwunderbar666/Python-RPi-MCP4922/raw/master/documentation/mcp4922sketch_schem.png)

#### Code

We need a library for the MCP4922 to run, luckily I wrote one and [you can get it here](https://github.com/mrwunderbar666/Python-RPi-MCP4922).

We follow the same testing logic:

```python
import RPi.GPIO as GPIO
import MCP4922 # Custom MCP4922 Library
import time

GPIO.setmode(GPIO.BCM) # Setting up the GPIO Mode

# DAC Setup
dac = MCP4922()

try:
    dac.setVoltage(0, 0) # Setting a starting voltage of 0 at channel A
    dac.setVoltage(1, 0) # Setting a starting voltage of 0 at channel B
    dac.setVoltage(0, 500) # Setting a Voltage value of 500, equals 402 mV, at channel A
    dac.setVoltage(1, 500) # Setting a Voltage value of 500, equals 402 mV, at channel B
    time.sleep(2) # Wait 2 seconds
    dac.setVoltage(0, 0) # Go back to 0, at channel A
    dac.setVoltage(1, 0) # Go back to 0, at channel B
    quit()
except KeyboardInterrupt:
    # Press CTRL + C to exit
    # Cleanup
    dac.setVoltage(0, 0)
    dac.setVoltage(1, 0)
    dac.shutdown(0)
    dac.shutdown(1)
    GPIO.cleanup()
    sys.exit(0)
    pass

```

#### The result looks like this:

And we can observer the beauty:

_Click to watch_

[![DAC Linear](https://github.com/mrwunderbar666/rpi-vumonitor-python/raw/master/docs/dac_lin.gif)](https://vid.me/R3IVR)

[![DAC Speedtest](https://github.com/mrwunderbar666/rpi-vumonitor-python/raw/master/docs/dac_speedtest.gif)](https://vid.me/Wm7bx)

## 6: Calibration

No matter which option you chose (PWM, DAC) you can use the code snippets above to calibrate and fine tune your VU Meters. Slowly increase the maximum PWM Duty Cycle or DAC Value until the VU Meter reaches its maximum deflection.

## 7: Getting System Stats using psutil
Now that we have calibrated the VU Meters we get very close to the finishing line. As we want the VU Meters to represent current system statistics, we have to extract the current system value and then translate it into a output value for the VU Meter.

There is a very handy python module called [psutil](https://github.com/giampaolo/psutil) which is great for getting all kinds of system statistics. It can extract network stats, CPU usage, temperature, disk read and write stats and even more. So from here, it really depends on what values you want to display with the VU Meters.

### TL;DR
I will walk through the code below but if you're not interested you can skip this and go to the [Github repository with the complete code](https://github.com/mrwunderbar666/rpi-vumonitor-python).

### CPU Usage

Let's have a look at the CPU usage and how to utilize psutil in python:

```python
import sys
import psutil # for monitoring system statistics

try:
    interval = 0 # First time, poll immediately
    while True:
        cpu_usage = psutil.cpu_percent(interval) # gauge the CPU usage and store it in a variable
        print(cpu_usage) # Print the current CPU Usage in Percent
        interval = 1 # poll every second
except (KeyboardInterrupt, SystemExit):
    sys.exit(0)
```

This snipped should print out the current CPU Usage in percent every second.

We can now enhance the code and combine it with the VU Monitor. This example is for DAC users:

```python
import sys
import psutil # for monitoring system statistics
import RPi.GPIO as GPIO
import MCP4922 # Custom MCP4922 Library

GPIO.setmode(GPIO.BCM) # Setting up the GPIO Mode

# DAC Setup
dac = MCP4922()

dac_max = 500 # Maximum DAC output, in this example 500 / 4096


try:
    interval = 0 # First time, poll immediately
    dac.setVoltage(0, 0) # Setting a starting voltage of 0 at channel A
    while True:
        cpu_usage = psutil.cpu_percent(interval) # gauge the CPU usage and store it in a variable
        print(cpu_usage) # Print the current CPU Usage in Percent
        dac_value = (cpu_usage / 100) * dac_max # calculate the dac value based on the CPU Usage in percent
        dac.SetVoltage(0, int(dac_value)) # output to the VU Meter
        interval = 1 # poll every second
except (KeyboardInterrupt, SystemExit):
    # Cleanup
    dac.setVoltage(0, 0)
    dac.setVoltage(1, 0)
    dac.shutdown(0)
    dac.shutdown(1)
    GPIO.cleanup()
    sys.exit(0)
```

This small snipped is already fully functional and makes your VU Meter needle move according to the current CPU Usage.
You can also adapt it for software / hardware PWM and change the `dac_max = 500` to e.g.  `pwm_max = 15` and adjust the setup according to the examples above.

### Network usage

This one is slightly trickier, because the linux system doesn't directly provide the current nework usage, but only the total bytes sent and received. So the code gets slightly more complex:

```python
import sys
import psutil # for monitoring system statistics
import time

def network_poll(interval):
    """Retrieve raw stats within an interval window."""
    net_before = psutil.net_io_counters()
    time.sleep(1) # wait one second
    net_after = psutil.net_io_counters()
    network_usage_received = net_after.bytes_recv - net_before.bytes_recv # Substracting the received bytes before and after
    network_usage_sent = net_after.bytes_sent - net_before.bytes_sent # Substracting the sent bytes before and after
    return network_usage_received, network_usage_sent

try:
    interval = 0 # First time, poll immediately
    while True:
        network_usage_received, network_usage_sent = network_poll(interval) # measure the network activitiy
        print(network_usage_received) # Print the current bytes received
        print(network_usage_sent) # Print the current bytes sent
        interval = 1 # poll every second
except (KeyboardInterrupt, SystemExit):
    sys.exit(0)
```

This will print the current network usage in bytes received and sent. It is not very human-readable, but for our purpose it does the job.

Now we apply the same principle as before, but this time, we have to translate the network usage differently. You could just assign one VU-Meter to represent incoming network traffic and a second one for the outgoing traffic. In the following example I will show a way to combine both stats into one by creating a coefficient:

```python
import sys
import psutil # for monitoring system statistics
import time

import RPi.GPIO as GPIO
import MCP4922 # Custom MCP4922 Library

GPIO.setmode(GPIO.BCM) # Setting up the GPIO Mode

# DAC Setup
dac = MCP4922()

# Network settings, maximum bandwidth is 15 MB/s so net_max = 15,000,000 bytes
net_max = 15000000

def net_coeffiecient(bytes_received_after, bytes_received_before, bytes_send_after, bytes_send_before):
    net_current = ((bytes_received_after - bytes_received_before) + ( bytes_send_after - bytes_send_before))
    x = (net_current / net_max)
    print("Current Network usage in percent is: {}" .format(x))
    # Clamping the maximum percentage to 100
    if x > 100:
        return 100
    elif x < 0:
        return 0
    else:
        return x
    return x

def network_poll(interval):
    """Retrieve raw stats within an interval window."""
    net_before = psutil.net_io_counters()
    time.sleep(1) # wait one second
    net_after = psutil.net_io_counters()
    # Feeding the values into the net coefficient function:
    network_usage = net_coeffiecient(net_after.bytes_recv, net_before.bytes_recv, net_after.bytes_sent, net_before.bytes_sent)
    # return the result 0 - 100 to the main function:
    return network_usage

try:
    interval = 0 # First time, poll immediately
    while True:
        network_usage = network_poll(interval) # measure the network activitiy
        dac_value = network_usage * dac_max # calculate the dac value based on the Netowrk Usage in percent
        dac.SetVoltage(0, int(dac_value)) # output to the VU Meter
        interval = 1 # poll every second
except (KeyboardInterrupt, SystemExit):
    # Cleanup
    dac.setVoltage(0, 0)
    dac.setVoltage(1, 0)
    dac.shutdown(0)
    dac.shutdown(1)
    GPIO.cleanup()
    sys.exit(0)
```

Now the VU-Meter will move according to the total network usage.

### Complete Code

The complete code for all different methods are in my [github repository](https://github.com/mrwunderbar666/rpi-vumonitor-python) and includes scripts for displaying CPU and Network statistics using different methods:
- software PWM
- hardware PWM
- MCP4725 DAC
- MCP4922 DAC

## 8: Linear vs Logarithmic Scaling

Now we are practically done, but if you have inspected my code carefully, you could see that I am not using a linear scale to output the VU Meter value.

I was using a linear scale at the beginning, but noticed that it was very hard to read low system activity on the VU-Meter. If my system was using the CPU of less than 10 %, I couldn't really tell if the needle was at 0 or not.

So I thought it might be better to have a [logarithmic growth function](http://www.math.umd.edu/~tjp/131%2011.1-2%20supplement%20logistic%20growth.pdf) as a base for the VU Meter Needle to move.

### You can compare the results here:

_Click to watch_

[![DAC Linear vs Logarithmic](https://github.com/mrwunderbar666/rpi-vumonitor-python/raw/master/docs/dac_lin_vs_log.gif)](https://vid.me/DoOnB)

### Some mathematical explanations

I am using a limited logistic growth function, that can be expressed as:

    B(x) = S - (S - B_0) \cdot e^{-k x}
    
_S_ = limit, _k_ = slope

This function will never reach its limit of _S_, which comes in handy given that we don't want the VU-Meter to go beyond its maximum deflection.

If we compare _B(t)_ function with a regular linear function, it looks like this:

![Figure 1: Linear vs logarithmic growth](https://github.com/mrwunderbar666/rpi-vumonitor-python/raw/master/docs/Figure_1.png)

Adjusting _k_ helps to flatten the slope a bit, so the effect is more subtle:

![Figure 2: Adjusted k](https://github.com/mrwunderbar666/rpi-vumonitor-python/raw/master/docs/Figure_2.png)

## 9: Wrapping up

So to implement everything with your Raspberry Pi, you can clone my repository:

```bash
cd ~
git clone https://github.com/mrwunderbar666/rpi-vumonitor-python.git
```

Make sure you have all the dependencies installed:

```bash
sudo apt-get install python-rpi.gpio
sudo pip install psutil
sudo pip install wiringpi
```

And if you want to use a DAC, check the respective repositories.

After the dependencies are running you can run one script with your preferred method:

```bash
cd rpi-vumonitor-python
sudo python pwm_vumonitor.py &
```

### Start at boot

If you want to launch the script automatically, you can do that with a shell script and add it to your crontab:

```bash
cd ~
nano startup.sh
```

Add the following code to the startup.sh file:

```bash
sudo python \home\USER\rpi-vumonitor-python\pwm_vumonitor.py &
```

and then add to your crontab via `sudo crontab -e`:

```bash
@reboot bash \home\USER\startup.sh
```


