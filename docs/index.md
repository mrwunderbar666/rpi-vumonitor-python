# Description
_Using Audio VU Meters to visualize CPU and Network usage of your Raspberry Pi._

Webinterfaces to monitor your RPi are neat and useful, but what if you want to have an analog display that physically shows you what your RPi is doing? 

There are many explanations out there that show how to use a small LCD Display to monitor your Raspberry Pi, but I haven't found any about using a VU meter.

This project is especially useful for people who salvage old HiFi equipment to create a casing for a Raspberry Pi. Use the old fashioned VU meters to give your raspberry pi a more hipster look :)

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

    I = V / R

Where I is the current, V is the voltage, and R is the resistance:

    \frac{V_(PowerSupply)}{R_(Meter)+R_{Trimpot)} = \frac{1.24 V}{659 \Omega} + 1190 \Omega} = 670 \mu A

This is useful to know if you have a different Voltage value from your power supply.

#### Using a 5 V Power Supply

Let's assume you have a 5 V power supply and want to get a ballpark estimation of the required resistance of your trimpots:

    R_(Trimpot) + R_(Meter) = \frac{V}{I}
    
    R_(Trimpot) = \frac{V}{I} - R_(Meter)

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

    V_(Effective) = V_(Total) * D
    
or:

    D = \frac{V_(Effective)}{V_(Total)}
    
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

The result looks like this:

# Insert GIF with jittery VU Meter

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

# Insert Gif of VU Meter with Wiring Pi

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

    MCP4725     RPi
    SCL         GPIO3 (Physical 5)
    SDA         GPIO2 (Physical 3)
    VDD         3.3 V (Physical 1)
    VSS         GND (Physical 6)
    VOUT        VU Meter Positive
    
It is a good idea to add resistors to the SCL and SDA connections and also to add a bypass capacitor from the 3.3 V rail to the MCP4725. In breadboard it would look like this:

![Breadboard 2: MCP4725 Circuit](https://github.com/mrwunderbar666/rpi-vumonitor-python/raw/master/docs/mcp4725_sketch_bb.png)

And here is a schematic view of the circuit:

![Schematic 2: MCP4725 Circuit](https://github.com/mrwunderbar666/rpi-vumonitor-python/raw/master/docs/mcp4725_sketch_schem.png)


