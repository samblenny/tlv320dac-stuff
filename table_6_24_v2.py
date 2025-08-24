# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024 Sam Blenny
"""
In the TLV320DAC datasheet, Table 6-24, "Analog Volume Control for Headphone
and Speaker Outputs" lists a lookup table to convert from analog gain dB to
register values suitable for storing in analog volume control registers:
- P1/R36=0x24 Left  Analog Volume to HPL (range 0 dB to -78 dB)
- P1/R37=0x25 Right Analog Volume to HPR (range 0 dB to -78 dB)
- P1/R38=0x26 Left  Analog Volume to SPK (range 0 dB to -78 dB)

The table values make a non-linear piecewise function:
1. 0 dB to -52.7 dB is almost a straight line, but it has some jitter on
   the order of ±0.3. Approximate formula: reg val = round((-1.99 * dB) - 0.2)
2. -52.7 dB to -78 dB looks like an exponential or parabolic curve
3. At the end, there's a constant line segment for -78.3 dB
"""


# ============================================================================
# == Start of lookup table based conversion implementation ===================
# ============================================================================


# These values are transcribed from TLV320DAC3100 datasheet Table 6-24.
TABLE_6_24 = (
      0,    #   0  Begin linear segment: round((-1.99 * dB) - 0.2)
     -0.5,  #   1
     -1,    #   2
     -1.5,  #   3
     -2,    #   4
     -2.5,  #   5
     -3,    #   6
     -3.5,  #   7
     -4,    #   8
     -4.5,  #   9
     -5,    #  10
     -5.5,  #  11
     -6,    #  12
     -6.5,  #  13
     -7,    #  14
     -7.5,  #  15
     -8,    #  16
     -8.5,  #  17
     -9,    #  18
     -9.5,  #  19
    -10,    #  20
    -10.5,  #  21
    -11,    #  22
    -11.5,  #  23
    -12,    #  24
    -12.5,  #  25
    -13,    #  26
    -13.5,  #  27
    -14,    #  28
    -14.5,  #  29
    -15,    #  30
    -15.5,  #  31
    -16,    #  32
    -16.5,  #  33
    -17,    #  34
    -17.5,  #  35
    -18.1,  #  36
    -18.6,  #  37
    -19.1,  #  38
    -19.6,  #  39
    -20.1,  #  40
    -20.6,  #  41
    -21.1,  #  42
    -21.6,  #  43
    -22.1,  #  44
    -22.6,  #  45
    -23.1,  #  46
    -23.6,  #  47
    -24.1,  #  48
    -24.6,  #  49
    -25.1,  #  50
    -25.6,  #  51
    -26.1,  #  52
    -26.6,  #  53
    -27.1,  #  54
    -27.6,  #  55
    -28.1,  #  56
    -28.6,  #  57
    -29.1,  #  58
    -29.6,  #  59
    -30.1,  #  60
    -30.6,  #  61
    -31.1,  #  62
    -31.6,  #  63
    -32.1,  #  64
    -32.6,  #  65
    -33.1,  #  66
    -33.6,  #  67
    -34.1,  #  68
    -34.6,  #  69
    -35.2,  #  70
    -35.7,  #  71
    -36.2,  #  72
    -36.7,  #  73
    -37.2,  #  74
    -37.7,  #  75
    -38.2,  #  76
    -38.7,  #  77
    -39.2,  #  78
    -39.7,  #  79
    -40.2,  #  80
    -40.7,  #  81
    -41.2,  #  82
    -41.7,  #  83
    -42.1,  #  84
    -42.7,  #  85
    -43.2,  #  86
    -43.8,  #  87
    -44.3,  #  88
    -44.8,  #  89
    -45.2,  #  90
    -45.8,  #  91
    -46.2,  #  92
    -46.7,  #  93
    -47.4,  #  94
    -47.9,  #  95
    -48.2,  #  96
    -48.7,  #  97
    -49.3,  #  98
    -50,    #  99
    -50.3,  # 100
    -51,    # 101
    -51.4,  # 102
    -51.8,  # 103
    -52.2,  # 104
    -52.7,  # 105  End linear segment: round((-1.99 * dB) - 0.2)
    -53.7,  # 106  Begin curved segment
    -54.2,  # 107
    -55.3,  # 108
    -56.7,  # 109
    -58.3,  # 110
    -60.2,  # 111
    -62.7,  # 112
    -64.3,  # 113
    -66.2,  # 114
    -68.7,  # 115
    -72.2,  # 116  End curved segment
    -78.3,  # 117  Begin constant segment -78.3 dB
    -78.3,  # 118
    -78.3,  # 119
    -78.3,  # 120
    -78.3,  # 121
    -78.3,  # 122
    -78.3,  # 123
    -78.3,  # 124
    -78.3,  # 125
    -78.3,  # 126
    -78.3,  # 127
)

def table_6_24_dB_to_uint7(dB):
    """
    Convert analog gain dB to 7-bit unsigned int to match datasheet Table 6-24.
    Valid gain dB range is -78.3 dB to 0 dB.
    """
    # Clip dB argument to fit in the valid range if it's too big or too small
    dB = max(-78.3, min(0, dB))
    # Loop through the table, looking for the lowest table index where the
    # target dB value is not greater than the table dB value
    result = 0
    for (table_uint7, table_dB) in enumerate(TABLE_6_24):
        if dB < table_dB:
            result = table_uint7
        elif dB == table_dB:
            result = table_uint7
            break
        else:
            break
    return result

def table_6_24_uint7_to_dB(u7):
    """
    Convert 7-bit unsigned int to analog gain to match datasheet Table 6-24.
    Valid values for u7 are integers in range 0 to 127.
    """
    return TABLE_6_24[max(0, min(127, int(u7)))]


# =============================================================================
# == End of lookup table based conversion implementation, start of test data ==
# =============================================================================

# These values are transcribed from TLV320DAC3100 datasheet Table 6-24.
# format: (Register Value for bits D6-D0, Analog Gain dB)
table_6_24 = (
    (  0,   0  ),  # Begin linear segment: round((-1.99 * dB) - 0.2)
    (  1,  -0.5),
    (  2,  -1  ),
    (  3,  -1.5),
    (  4,  -2  ),
    (  5,  -2.5),
    (  6,  -3  ),
    (  7,  -3.5),
    (  8,  -4  ),
    (  9,  -4.5),
    ( 10,  -5  ),
    ( 11,  -5.5),
    ( 12,  -6  ),
    ( 13,  -6.5),
    ( 14,  -7  ),
    ( 15,  -7.5),
    ( 16,  -8  ),
    ( 17,  -8.5),
    ( 18,  -9  ),
    ( 19,  -9.5),
    ( 20, -10  ),
    ( 21, -10.5),
    ( 22, -11  ),
    ( 23, -11.5),
    ( 24, -12  ),
    ( 25, -12.5),
    ( 26, -13  ),
    ( 27, -13.5),
    ( 28, -14  ),
    ( 29, -14.5),
    ( 30, -15  ),
    ( 31, -15.5),
    ( 32, -16  ),
    ( 33, -16.5),
    ( 34, -17  ),
    ( 35, -17.5),
    ( 36, -18.1),
    ( 37, -18.6),
    ( 38, -19.1),
    ( 39, -19.6),
    ( 40, -20.1),
    ( 41, -20.6),
    ( 42, -21.1),
    ( 43, -21.6),
    ( 44, -22.1),
    ( 45, -22.6),
    ( 46, -23.1),
    ( 47, -23.6),
    ( 48, -24.1),
    ( 49, -24.6),
    ( 50, -25.1),
    ( 51, -25.6),
    ( 52, -26.1),
    ( 53, -26.6),
    ( 54, -27.1),
    ( 55, -27.6),
    ( 56, -28.1),
    ( 57, -28.6),
    ( 58, -29.1),
    ( 59, -29.6),
    ( 60, -30.1),
    ( 61, -30.6),
    ( 62, -31.1),
    ( 63, -31.6),
    ( 64, -32.1),
    ( 65, -32.6),
    ( 66, -33.1),
    ( 67, -33.6),
    ( 68, -34.1),
    ( 69, -34.6),
    ( 70, -35.2),
    ( 71, -35.7),
    ( 72, -36.2),
    ( 73, -36.7),
    ( 74, -37.2),
    ( 75, -37.7),
    ( 76, -38.2),
    ( 77, -38.7),
    ( 78, -39.2),
    ( 79, -39.7),
    ( 80, -40.2),
    ( 81, -40.7),
    ( 82, -41.2),
    ( 83, -41.7),
    ( 84, -42.1),
    ( 85, -42.7),
    ( 86, -43.2),
    ( 87, -43.8),
    ( 88, -44.3),
    ( 89, -44.8),
    ( 90, -45.2),
    ( 91, -45.8),
    ( 92, -46.2),
    ( 93, -46.7),
    ( 94, -47.4),
    ( 95, -47.9),
    ( 96, -48.2),
    ( 97, -48.7),
    ( 98, -49.3),
    ( 99, -50  ),
    (100, -50.3),
    (101, -51  ),
    (102, -51.4),
    (103, -51.8),
    (104, -52.2),
    (105, -52.7),  # End linear segment: round((-1.99 * dB) - 0.2)
    (106, -53.7),  # Begin curved segment
    (107, -54.2),
    (108, -55.3),
    (109, -56.7),
    (110, -58.3),
    (111, -60.2),
    (112, -62.7),
    (113, -64.3),
    (114, -66.2),
    (115, -68.7),
    (116, -72.2),  # End curved segment
    (117, -78.3),  # Begin constant segment -78.3 dB
    (118, -78.3),
    (119, -78.3),
    (120, -78.3),
    (121, -78.3),
    (122, -78.3),
    (123, -78.3),
    (124, -78.3),
    (125, -78.3),
    (126, -78.3),
    (127, -78.3),
)


# =============================================================================
# == End of test data, start of test Code =====================================
# =============================================================================

# Test dB to uint7 conversion function by comparing to values from the table
print(" Gain_dB  Table    Computed  Reg Val")
print("          Reg Val  Reg Val   Diff")
for (table_val, table_dB) in table_6_24:
    uint7 = table_6_24_dB_to_uint7(table_dB)
    dB_str = str("%.1f" % table_dB)
    diff = str(uint7 - table_val)
    print(f"{dB_str:>5} dB     {table_val:3d}    {uint7:3d}      {diff:>3}")
print()

# Test uint7 to dB conversion function by comparing to values from the table
print(" Table    Table    Computed  Gain_dB")
print(" Reg Val  Gain_dB  Gain_dB   Diff")
for (table_val, table_dB) in table_6_24:
    computed_dB = table_6_24_uint7_to_dB(table_val)
    t_dB = str("%.1f" % table_dB)
    c_dB = str("%.1f" % computed_dB)
    diff = str("%.1f" % (computed_dB - table_dB))
    print(f"{table_val:3d}       {t_dB:>5}    {c_dB:>5}      {diff:>3}")


# The output below is from running the two test loops above.
#
# The final columns are comparing expected values from the table to values from
# table_6_24_dB_to_uint7() and table_6_24_uint7_to_dB(). A difference of 0
# means the computed values match the table.
#
# Note that the values 118-127 in the dB to register-value direction
# have a non-zero difference. This is expected since the table is giving us a
# [multivalued function](https://en.wikipedia.org/wiki/Multivalued_function),
# because of the final constant segment where register values 117-127 all map
# to a single gain value (-78.3 dB). The difference is okay because we're using
# an effectively equivalent single-valued function to compute register-value
# as a function of gain dB.
"""
$ python3 table_6_24_v2.py
 Gain_dB  Table    Computed  Reg Val
          Reg Val  Reg Val   Diff
  0.0 dB       0      0        0
 -0.5 dB       1      1        0
 -1.0 dB       2      2        0
 -1.5 dB       3      3        0
 -2.0 dB       4      4        0
 -2.5 dB       5      5        0
 -3.0 dB       6      6        0
 -3.5 dB       7      7        0
 -4.0 dB       8      8        0
 -4.5 dB       9      9        0
 -5.0 dB      10     10        0
 -5.5 dB      11     11        0
 -6.0 dB      12     12        0
 -6.5 dB      13     13        0
 -7.0 dB      14     14        0
 -7.5 dB      15     15        0
 -8.0 dB      16     16        0
 -8.5 dB      17     17        0
 -9.0 dB      18     18        0
 -9.5 dB      19     19        0
-10.0 dB      20     20        0
-10.5 dB      21     21        0
-11.0 dB      22     22        0
-11.5 dB      23     23        0
-12.0 dB      24     24        0
-12.5 dB      25     25        0
-13.0 dB      26     26        0
-13.5 dB      27     27        0
-14.0 dB      28     28        0
-14.5 dB      29     29        0
-15.0 dB      30     30        0
-15.5 dB      31     31        0
-16.0 dB      32     32        0
-16.5 dB      33     33        0
-17.0 dB      34     34        0
-17.5 dB      35     35        0
-18.1 dB      36     36        0
-18.6 dB      37     37        0
-19.1 dB      38     38        0
-19.6 dB      39     39        0
-20.1 dB      40     40        0
-20.6 dB      41     41        0
-21.1 dB      42     42        0
-21.6 dB      43     43        0
-22.1 dB      44     44        0
-22.6 dB      45     45        0
-23.1 dB      46     46        0
-23.6 dB      47     47        0
-24.1 dB      48     48        0
-24.6 dB      49     49        0
-25.1 dB      50     50        0
-25.6 dB      51     51        0
-26.1 dB      52     52        0
-26.6 dB      53     53        0
-27.1 dB      54     54        0
-27.6 dB      55     55        0
-28.1 dB      56     56        0
-28.6 dB      57     57        0
-29.1 dB      58     58        0
-29.6 dB      59     59        0
-30.1 dB      60     60        0
-30.6 dB      61     61        0
-31.1 dB      62     62        0
-31.6 dB      63     63        0
-32.1 dB      64     64        0
-32.6 dB      65     65        0
-33.1 dB      66     66        0
-33.6 dB      67     67        0
-34.1 dB      68     68        0
-34.6 dB      69     69        0
-35.2 dB      70     70        0
-35.7 dB      71     71        0
-36.2 dB      72     72        0
-36.7 dB      73     73        0
-37.2 dB      74     74        0
-37.7 dB      75     75        0
-38.2 dB      76     76        0
-38.7 dB      77     77        0
-39.2 dB      78     78        0
-39.7 dB      79     79        0
-40.2 dB      80     80        0
-40.7 dB      81     81        0
-41.2 dB      82     82        0
-41.7 dB      83     83        0
-42.1 dB      84     84        0
-42.7 dB      85     85        0
-43.2 dB      86     86        0
-43.8 dB      87     87        0
-44.3 dB      88     88        0
-44.8 dB      89     89        0
-45.2 dB      90     90        0
-45.8 dB      91     91        0
-46.2 dB      92     92        0
-46.7 dB      93     93        0
-47.4 dB      94     94        0
-47.9 dB      95     95        0
-48.2 dB      96     96        0
-48.7 dB      97     97        0
-49.3 dB      98     98        0
-50.0 dB      99     99        0
-50.3 dB     100    100        0
-51.0 dB     101    101        0
-51.4 dB     102    102        0
-51.8 dB     103    103        0
-52.2 dB     104    104        0
-52.7 dB     105    105        0
-53.7 dB     106    106        0
-54.2 dB     107    107        0
-55.3 dB     108    108        0
-56.7 dB     109    109        0
-58.3 dB     110    110        0
-60.2 dB     111    111        0
-62.7 dB     112    112        0
-64.3 dB     113    113        0
-66.2 dB     114    114        0
-68.7 dB     115    115        0
-72.2 dB     116    116        0
-78.3 dB     117    117        0
-78.3 dB     118    117       -1
-78.3 dB     119    117       -2
-78.3 dB     120    117       -3
-78.3 dB     121    117       -4
-78.3 dB     122    117       -5
-78.3 dB     123    117       -6
-78.3 dB     124    117       -7
-78.3 dB     125    117       -8
-78.3 dB     126    117       -9
-78.3 dB     127    117      -10

 Table    Table    Computed  Gain_dB
 Reg Val  Gain_dB  Gain_dB   Diff
  0         0.0      0.0      0.0
  1        -0.5     -0.5      0.0
  2        -1.0     -1.0      0.0
  3        -1.5     -1.5      0.0
  4        -2.0     -2.0      0.0
  5        -2.5     -2.5      0.0
  6        -3.0     -3.0      0.0
  7        -3.5     -3.5      0.0
  8        -4.0     -4.0      0.0
  9        -4.5     -4.5      0.0
 10        -5.0     -5.0      0.0
 11        -5.5     -5.5      0.0
 12        -6.0     -6.0      0.0
 13        -6.5     -6.5      0.0
 14        -7.0     -7.0      0.0
 15        -7.5     -7.5      0.0
 16        -8.0     -8.0      0.0
 17        -8.5     -8.5      0.0
 18        -9.0     -9.0      0.0
 19        -9.5     -9.5      0.0
 20       -10.0    -10.0      0.0
 21       -10.5    -10.5      0.0
 22       -11.0    -11.0      0.0
 23       -11.5    -11.5      0.0
 24       -12.0    -12.0      0.0
 25       -12.5    -12.5      0.0
 26       -13.0    -13.0      0.0
 27       -13.5    -13.5      0.0
 28       -14.0    -14.0      0.0
 29       -14.5    -14.5      0.0
 30       -15.0    -15.0      0.0
 31       -15.5    -15.5      0.0
 32       -16.0    -16.0      0.0
 33       -16.5    -16.5      0.0
 34       -17.0    -17.0      0.0
 35       -17.5    -17.5      0.0
 36       -18.1    -18.1      0.0
 37       -18.6    -18.6      0.0
 38       -19.1    -19.1      0.0
 39       -19.6    -19.6      0.0
 40       -20.1    -20.1      0.0
 41       -20.6    -20.6      0.0
 42       -21.1    -21.1      0.0
 43       -21.6    -21.6      0.0
 44       -22.1    -22.1      0.0
 45       -22.6    -22.6      0.0
 46       -23.1    -23.1      0.0
 47       -23.6    -23.6      0.0
 48       -24.1    -24.1      0.0
 49       -24.6    -24.6      0.0
 50       -25.1    -25.1      0.0
 51       -25.6    -25.6      0.0
 52       -26.1    -26.1      0.0
 53       -26.6    -26.6      0.0
 54       -27.1    -27.1      0.0
 55       -27.6    -27.6      0.0
 56       -28.1    -28.1      0.0
 57       -28.6    -28.6      0.0
 58       -29.1    -29.1      0.0
 59       -29.6    -29.6      0.0
 60       -30.1    -30.1      0.0
 61       -30.6    -30.6      0.0
 62       -31.1    -31.1      0.0
 63       -31.6    -31.6      0.0
 64       -32.1    -32.1      0.0
 65       -32.6    -32.6      0.0
 66       -33.1    -33.1      0.0
 67       -33.6    -33.6      0.0
 68       -34.1    -34.1      0.0
 69       -34.6    -34.6      0.0
 70       -35.2    -35.2      0.0
 71       -35.7    -35.7      0.0
 72       -36.2    -36.2      0.0
 73       -36.7    -36.7      0.0
 74       -37.2    -37.2      0.0
 75       -37.7    -37.7      0.0
 76       -38.2    -38.2      0.0
 77       -38.7    -38.7      0.0
 78       -39.2    -39.2      0.0
 79       -39.7    -39.7      0.0
 80       -40.2    -40.2      0.0
 81       -40.7    -40.7      0.0
 82       -41.2    -41.2      0.0
 83       -41.7    -41.7      0.0
 84       -42.1    -42.1      0.0
 85       -42.7    -42.7      0.0
 86       -43.2    -43.2      0.0
 87       -43.8    -43.8      0.0
 88       -44.3    -44.3      0.0
 89       -44.8    -44.8      0.0
 90       -45.2    -45.2      0.0
 91       -45.8    -45.8      0.0
 92       -46.2    -46.2      0.0
 93       -46.7    -46.7      0.0
 94       -47.4    -47.4      0.0
 95       -47.9    -47.9      0.0
 96       -48.2    -48.2      0.0
 97       -48.7    -48.7      0.0
 98       -49.3    -49.3      0.0
 99       -50.0    -50.0      0.0
100       -50.3    -50.3      0.0
101       -51.0    -51.0      0.0
102       -51.4    -51.4      0.0
103       -51.8    -51.8      0.0
104       -52.2    -52.2      0.0
105       -52.7    -52.7      0.0
106       -53.7    -53.7      0.0
107       -54.2    -54.2      0.0
108       -55.3    -55.3      0.0
109       -56.7    -56.7      0.0
110       -58.3    -58.3      0.0
111       -60.2    -60.2      0.0
112       -62.7    -62.7      0.0
113       -64.3    -64.3      0.0
114       -66.2    -66.2      0.0
115       -68.7    -68.7      0.0
116       -72.2    -72.2      0.0
117       -78.3    -78.3      0.0
118       -78.3    -78.3      0.0
119       -78.3    -78.3      0.0
120       -78.3    -78.3      0.0
121       -78.3    -78.3      0.0
122       -78.3    -78.3      0.0
123       -78.3    -78.3      0.0
124       -78.3    -78.3      0.0
125       -78.3    -78.3      0.0
126       -78.3    -78.3      0.0
127       -78.3    -78.3      0.0
"""
