import sys

import math
import numpy
import os
import util

from system import System

class Text(System):

    def __init__(self, noise_level):
        super(Text, self).__init__(noise_level)
        self.message = None

        # We allow a full ASCII alphabet
        alphabet = [chr(i) for i in range(255)]

        # We want to map each letter to a voltage level.  For n items
        # in the alphabet, we map letters in order to 0.0,
        # 0.0+1/(n-1), 0.0+2/(n-1), etc.
        #
        # I.e., an 11-character setup might look like:
        #  A = 0.0
        #  B = 0.1
        #  C = 0.2
        #    ...
        #  K = 1.0
        self.alphabet = {}
        diff = 1.0 / (len(alphabet) - 1)
        voltage = 0.0
        for a in sorted(alphabet):
            self.alphabet[a] = voltage
            voltage += diff
            if voltage > 1.0: # deal with rounding on final element
                voltage = 1.0

        # We also want a reverse dict to do the decoding
        self.reverse_alphabet = {v: k for k, v in self.alphabet.items()}

    # Set the message as long as its valid
    def set_data(self, message):
        for c in message:
            if c not in self.alphabet:
                print("Invalid message")
                return
        self.message = message

    # Convert characters to floats using the predefined dictionary.
    def get_analog_data(self):
        if self.message is None:
            print("Cannot get data without setting message")
            sys.exit(-1)
        floats = [self.alphabet[c] for c in self.message]
        return floats

    # Get the analog data and convert that to bits
    def get_digital_data(self):
        floats = self.get_analog_data()
        bits = util.floats_to_bits(floats)
        return bits

    # Print the analog output, using the reverse dictionary to get the
    # characters that correspond to each float.
    def output_analog(self, data):
        s = ""
        for f in data:
            f_key = min(self.reverse_alphabet, key=lambda x:math.fabs(x-f))
            c = self.reverse_alphabet[f_key]
            s += c
        print(s)

    # Print the digital output by turning the bits pack into floats
    # and then calling output_analog
    def output_digital(self, data):
        floats = util.bits_to_floats(data)
        self.output_analog(floats)
