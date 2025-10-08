'''
sdr_service.py
Captures live raw IQ data from an SDR (Software Defined Radio) device and returns it as a raw data stream.
'''

# TABLE BELOW FOR LATER
# add a data structure that stores various SDR urls, by different geographical locations
# also need to change frequency frequently (4 - 90 MHz)
# also need to hash the samples, should not use raw amplitude, SHA256 or Keccak
# also some bands are better during different times of the day, need to research more on this

# CURRENT IMPLEMENTATION
# just open up the SDR stream on a system and capture the audio with webcam

import redis
import numpy as np


r = redis.Redis(host='localhost', port=6379, db=0)
