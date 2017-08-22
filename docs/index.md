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
1. Connect your VU Meter to your bench power supply and have at least 3 trimpots in series, but do not switch on your power supply yet. My bench power supply lowest reliable voltage is 1.24 V. If your's can go lower, it is even better.
1. Set your trimpots to the highest resistance
1. Attach your multimeter to the positive and negative terminals of your VU Meter
1. Switch on your power supply
1. Slowly decrease the resistance of your trimpots until your VU Meter shows maximum deflection (needle goes towards the maximum value). 
1. Measure the voltage across the VU Meter. In my case: 0.443 V or 443 mV
1. Measure the resistance across all your trimpots. In my case: 1190 Ω

#### VU Meter Gauging Circuit
![Schematic 1: VU Meter Gauging Circuit](https://cdn.hackaday.io/images/4330441502869675844.png)

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

### Driving the VU Meter by the Raspberry Pi

Now that we understand the VU Meters, let's have a look at how to connect and drive them from the Raspberry Pi.

By default the RPi has a 3.3 V or 5 V supply rail. That would be total overkill for the sensitive VU Meters. A regular GPIO Pin delivers 3.3 V if it is set to "HIGH", so that would be also too much and not variable.

So let's have a look at how we can get that 3.3 V to a much lower value and also change the output value:

#### PWM (Pulse Width Modulation)

The simplest way to control the voltage (and effective current) applied to the VU Meter is by using PWM (Pulse Width Modulation).

There are two ways of creating a PWM Signal from the RPI:

1. Software PWM (fast & simple, can use almost any GPIO)
2. Hardware PWM (special python module, can use limited GPIOs)

In the steps below, I will go into detail for both ways.

#### DAC (Digital to Analog Converter)

The RPi doesn't have any DAC integrated, so we need to hook one up. There are plenty of choices but also some considerations to make: 

we need to have low voltages between 0 - 500 mV, and the supply source provides 3.3 V. That means we need a decent resolution.

The resolution (or steps) of the DAC depends of its bit value.

The cheaper DACs provide an 8-bit resolution, which means 256 steps:

    \frac{3300mV}{256} = 12.8 mV

So with that we can control the voltage in 12.8 mV steps. A bit too low for my taste.

At 10-bit we get 1024 steps:

    \frac{3300mV}{1024} = 3.32 mV


So with that we can control the voltage in 3.3 mV steps. Much better, but let's take this further.

At 12-bit we have 4096 steps of resolution:

    \frac{3300mV}{4096} = 0.8 mV


12-bit seems right, because it let's us control the VU Meter in around 1 mV steps. Which provides a quite accurate of the needle at the end.

I will go into different DACs at a later point. E.g. how many VU Meters we want to control is another consideration for choosing a DAC.
