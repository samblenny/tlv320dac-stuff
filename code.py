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
import supervisor
import time

from adafruit_tlv320 import TLV320DAC3100


# DAC and Synthesis parameters
SAMPLE_RATE = const(11025)
CHAN_COUNT  = const(2)
BUFFER_SIZE = const(1024)

# DAC volume limits
DV_MIN = -63.5
DV_MAX = 24.0

# Headphone volume limits
HV_MIN = -78.3
HV_MAX = 0

# Headphone gain limits
HG_MIN = 0
HG_MAX = 9


def init_dac_audio_synth(i2c):
    """Configure TLV320 I2S DAC for audio output and make a Synthesizer.

    :param i2c: a reference to board.I2C()
    :return: tuple(dac: TLV320DAC3100, audio: I2SOut, synth: Synthesizer)
    """
    # 1. Reset DAC (reset is active low)
    rst = DigitalInOut(PERIPH_RESET)
    rst.direction = Direction.OUTPUT
    rst.value = False
    time.sleep(0.1)
    rst.value = True
    time.sleep(0.05)
    # 2. Configure sample rate, bit depth, and output port
    dac = TLV320DAC3100(i2c)
    dac.configure_clocks(sample_rate=SAMPLE_RATE, bit_depth=16)
    dac.speaker_output = False
    dac.headphone_output = True
    # 4. Initialize I2S for Fruit Jam rev D
    audio = I2SOut(bit_clock=I2S_BCLK, word_select=I2S_WS, data=I2S_DIN)
    # 5. Configure synthio patch to generate audio
    vca = synthio.Envelope(
        attack_time=0, decay_time=0, sustain_level=1.0,
        release_time=0, attack_level=1.0
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

    dv = dac.dac_volume           # default DAC volume
    hv = dac.headphone_volume     # default headphone analog volume
    hg = dac.headphone_left_gain  # default headphone amp gain
    note = 60
    synth.press(note)
    # Check for unbuffered keystroke input on the USB serial console
    while True:
        time.sleep(0.01)
        if supervisor.runtime.serial_bytes_available:
            while supervisor.runtime.serial_bytes_available:
                c = sys.stdin.read(1)
                if c == 'q':
                    # Q = DAC Volume UP
                    dv = min(DV_MAX, max(DV_MIN, dv + 1))
                    dac.dac_volume = dv
                    print(f"dv = {dv:.1f} ({dac.dac_volume:.1f})")
                elif c == 'z':
                    # Z = DAC Volume DOWN
                    dv = min(DV_MAX, max(DV_MIN, dv - 1))
                    dac.dac_volume = dv
                    print(f"dv = {dv:.1f} ({dac.dac_volume:.1f})")
                elif c == 'w':
                    # W = Headphone Volume UP
                    hv = min(HV_MAX, max(HV_MIN, hv + 1))
                    dac.headphone_volume = hv
                    print(f"hv = {hv:.1f} ({dac.headphone_volume:.1f})")
                elif c == 'x':
                    # X = Headphone Volume DOWN
                    hv = min(HV_MAX, max(HV_MIN, hv - 1))
                    dac.headphone_volume = hv
                    print(f"hv = {hv:.1f} ({dac.headphone_volume:.1f})")
                elif c == 'e':
                    # E = Headphone Amp Gain UP
                    hg = min(HG_MAX, max(HG_MIN, hg + 1))
                    dac.headphone_left_gain = hg
                    dac.headphone_right_gain = hg
                    print(f"hg = {hg:.1f} ({dac.headphone_left_gain})")
                elif c == 'c':
                    # C = Headphone Amp Gain DOWN
                    hg = min(HG_MAX, max(HG_MIN, hg - 1))
                    dac.headphone_left_gain = hg
                    dac.headphone_right_gain = hg
                    print(f"hg = {hg:.1f} ({dac.headphone_left_gain})")


main()
