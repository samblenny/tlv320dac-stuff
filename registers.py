# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024 Sam Blenny
"""
Scratchpad for documenting and converting TLV320 registers.

The datasheet specifies values in a mix of base-10 integers, base-10 decibels,
base-2 bitfields, base-16 addresses, and so on. The main point of this file is
to gather datasheet details relevant to volume control and normalize things
into base-10 or base-16 so I can compare them to the library source code.
"""

# p. 75 Table 6-77 Page 0 / Register 65 (0x41): DAC Left Volume Control
# p. 76 Table 6-78 Page 0 / Register 66 (0x42): DAC Right Volume Control
# bits D7-D0, R/W, reset value = 0b0000_0000
# (tables 6-77 (L DAC) and 6-78 (R DAC) have exactly the same values)
reg_65_0x41 = reg_66_0x42 = [
    (0b0111_1111, "-", 0b0011_0001, "reserved"),
    (0b0011_0000, "24 dB"),
    (0b0010_1111, "23.5 dB"),
    (0b0010_1110, "23 dB"),
    ("..."),
    (0b0000_0001, "0.5 dB"),
    (0b0000_0000, "0 dB"),
    (0b1111_1111, "–0.5 dB"),
    ("..."),
    (0b1000_0010, "–63 dB"),
    (0b1000_0001, "–63.5 dB"),
    (0b1000_0000, "reserved"),
]

def convert_DAC_LR_dB(dB):
    # Convert DAC volume dB in range -63.5..24 to int8 in range -127..48
    # See datasheet Table 6-77 (DAC L volume) and Table 6-78 (DAC R volume)
    scaled_dB = round(dB * 2)
    clipped_dB = max(-127, min(48, scaled_dB))  # range: (-63.5 * 2)...(24 * 2)
    int8_dB = clipped_dB & 0xff
    return int8_dB

def check_tables_6_77_and_6_78():
    print("Table 6-77 Register 65 (0x41) (same as Table 6-78):")
    print("\n".join(["  " + str(n) for n in reg_65_0x41]))
    print()
    print("Output of convert_DAC_LR_dB() function:")
    for n in [25, 24, 23.5, 0.5, 0, -0.5, -63, -63.5, -64]:
        int8_dB = convert_DAC_LR_dB(n)
        print(f"{str(int8_dB):>5s} = convert_DAC_LR_dB({n:+5.1f})")

check_tables_6_77_and_6_78()
"""
Table 6-77 Register 65 (0x41) (same as Table 6-78):
  (127, '-', 49, 'reserved')
  (48, '24 dB')
  (47, '23.5 dB')
  (46, '23 dB')
  ...
  (1, '0.5 dB')
  (0, '0 dB')
  (255, '–0.5 dB')
  ...
  (130, '–63 dB')
  (129, '–63.5 dB')
  (128, 'reserved')

Output of convert_DAC_LR_dB() function:
   48 = convert_DAC_LR_dB(+25.0)
   48 = convert_DAC_LR_dB(+24.0)
   47 = convert_DAC_LR_dB(+23.5)
    1 = convert_DAC_LR_dB( +0.5)
    0 = convert_DAC_LR_dB( +0.0)
  255 = convert_DAC_LR_dB( -0.5)
  130 = convert_DAC_LR_dB(-63.0)
  129 = convert_DAC_LR_dB(-63.5)
  129 = convert_DAC_LR_dB(-64.0)
"""

# This conversion math matches Page0Registers._set_channel_volume() in
# Adafruit_CircuitPython_TLV320/adafruit_tlv320.py.
# Page0Registers._set_channel_volume() is called by:
#  - TLV320DAC3100.__init__()
#  - Page0Registers.left_dac_channel_volume(self, db: float)
#  - Page0Registers.right_dac_channel_volume(self, db: float)
