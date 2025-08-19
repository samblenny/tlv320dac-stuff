# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2025 Sam Blenny
#
from audiobusio import I2SOut
from board import (
    I2C, I2S_BCLK, I2S_DIN, I2S_MCLK, I2S_WS, PERIPH_RESET
)
from digitalio import DigitalInOut, Direction, Pull
import displayio
import gc
from micropython import const
import os
import synthio
import sys
from time import sleep

from adafruit_tlv320 import TLV320DAC3100


# DAC and Synthesis parameters
SAMPLE_RATE = const(11025)
CHAN_COUNT  = const(2)
BUFFER_SIZE = const(1024)
#==============================================================
# CAUTION! When this is set to True, the headphone jack will
# send a line-level output suitable use with a mixer or powered
# speakers, but that will be _way_ too loud for earbuds. For
# finer control of volume, you can set dac.dac_volume below.
LINE_LEVEL  = const(False)
#==============================================================


def init_dac_audio_synth(i2c):
    # Configure TLV320 I2S DAC for audio output and make a Synthesizer.
    # - i2c: a reference to board.I2C()
    # - returns tuple: (dac: TLV320DAC3100, audio: I2SOut, synth: Synthesizer)
    #
    # 1. Reset DAC (reset is active low)
    rst = DigitalInOut(PERIPH_RESET)
    rst.direction = Direction.OUTPUT
    rst.value = False
    sleep(0.1)
    rst.value = True
    sleep(0.05)
    # 2. Configure sample rate, bit depth, and output port
    dac = TLV320DAC3100(i2c)
    dac.configure_clocks(sample_rate=SAMPLE_RATE, bit_depth=16)
    dac.speaker_mute = True
    dac.headphone_output = True
    # 3. Set volume for for line-level or headphone level
    if LINE_LEVEL:
        # This gives a line output level suitable for plugging into a mixer or
        # the AUX input of a powered speaker (THIS IS TOO LOUD FOR HEADPHONES!)
        dac.dac_volume = -44
        dac.headphone_volume = -64
    else:
        # This is a reasonable volume for my cheap JVC Gumy earbuds. They tend
        # to be louder than other headphones, so probably this ought to be a
        # generally safe volume level. For headphones that need a stronger
        # signal, carefully increase dac_volume (closer to 0 is louder).
        dac.dac_volume = -58
        dac.headphone_volume = -64
    # 4. Initialize I2S for Fruit Jam rev D
    print("Using default I2S pin definitions (board rev D or newer)")
    audio = I2SOut(bit_clock=I2S_BCLK, word_select=I2S_WS, data=I2S_DIN)
    # 5. Configure synthio patch to generate audio
    vca = synthio.Envelope(
        attack_time=0.002, decay_time=0.01, sustain_level=0.4,
        release_time=0, attack_level=0.6
    )
    synth = synthio.Synthesizer(
        sample_rate=SAMPLE_RATE, channel_count=CHAN_COUNT, envelope=vca
    )
    audio.play(synth)
    return (dac, audio, synth)


def main():
    # Turn off the default DVI display to free up CPU
    displayio.release_displays()
    gc.collect()

    # Set up the audio stuff for a basic synthesizer
    i2c = I2C()
    (dac, audio, synth) = init_dac_audio_synth(i2c)

    while True:
        for note in range(60, 73):
            synth.press(note)
            time.sleep(0.8)
            synth.release(note)
            time.sleep(0.2)

main()
