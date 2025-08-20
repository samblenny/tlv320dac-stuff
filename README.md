<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: Copyright 2025 Sam Blenny -->
# TLV320DAC Stuff

**DRAFT: WORK IN PROGRESS**

This is a scratch repo for notes and experiments to understand how volume
control works on the TLV320DAC3100 I2S DAC used in the Adafruit Fruit Jam
board.

Links:
- [Datasheet pdf](https://cdn-learn.adafruit.com/assets/assets/000/136/051/original/TLV320DAC3100_Low-Power_Stereo_Audio_DAC_With_Audio_Processing_and_Mono_Class-D_Speaker_Amplifier_datasheet_%28Rev._C%29_-_tlv320dac3100.pdf)
- [Adafruit_TLV320_I2S](https://github.com/adafruit/Adafruit_TLV320_I2S)
   Arduino library code
- [Adafruit_CircuitPython_TLV320](https://github.com/adafruit/Adafruit_CircuitPython_TLV320)
   CircuitPython library code (aka adafruit_tlv320)
- adafruit_tlv320 (CircuitPython library) [documentation](https://docs.circuitpython.org/projects/tlv320/en/latest/)
- Adafruit Forum discussion of [Fruit Jam DAC issues](https://forums.adafruit.com/viewtopic.php?t=219717)


## Math with Decibels (dB)

These formulas for power and amplitude dB ratios are from Art of Electronics,
third edition, section 1.3.2.

Formula for ratio between the **power** (Watts) of two signals (P1 and P2) in
decibels (dB):

```
dB = 10 * log10(P2 / P1)
```

Formula for ratio between the **amplitude** (Volts) for two signals (A1 and A2)
in decibels (dB):

```
dB = 20 * log10(A2 / A1)
```

By way of some basic algebra, we can derive a formula to convert dBV to peak
voltage (dBV reference value is 1V). Since we're using dBV, we know that A1 is
1V. Also, pow(10, n) is the inverse function of log10(n).

These are the steps to solve the amplitude formula for A2 as a function of dB:
1. `dB = 20 * log10(A2 / A1)`
2. `dB = 20 * log10(A2 / 1)`
3. `dB = 20 * log10(A2)`
4. `dB / 20 = log10(A2)`
5. `pow(10, dB / 20) = A2`
6. `A2 = pow(10, dB / 20)`

For example:
```python
>>> def volts(dBV):
...     return pow(10, dBV / 20)
...
>>> volts(dBV=-10)
0.31622776601683794
```


## Line-Level and Headphone-Level Voltages

The TLV320 has various settings for the voltage level and amplifier gain. I
mostly care about the headphone jack, so I need to know what voltage ranges are
appropriate for consumer line-level and headphone level output.

1. According to various online sources, consumer line-level is generally about
   -10dBV, which means 10 dB below a reference voltage of 1 Volt. By
   calculating `pow(10, -10/20)`, we can see that -10dBV is equivalent to an
   amplitude of 0.32V.

2. According to
   [this Apple Support page](https://support.apple.com/en-us/108351),
   modern Macs with headphone output jacks adapt to the impedance of connected
   headphones. For low impedance headphones (under 150 ohms), the output level
   is up to 1.25V RMS. For high impedance headphones of 150 to 1k ohms, the
   output level is up to 3V RMS. Generally, small cheap headphones are low
   impedance, and large over-the-ear headphones are high impedance.
