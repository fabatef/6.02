#!/usr/bin/python

'''Defines the Sender class.  The main function of this class is to
take an array of bits (preamble + data) to modulated voltage samples,
which will then be sent over the channel.'''

import numpy
import sys

import util

class Sender:

    ON_OFF = 0

    def __init__(self, frequency, config):
        # Set various options
        self.key_type = config.key_type
        self.fc = frequency
        self.sample_rate = config.sample_rate

        # Source is set explicitly later, because a single sender
        # can be used for multiple sources.
        self.source = None 

        # Set the appropriate voltage levels for 0 and 1 based on the
        # signaling type
        if self.key_type == Sender.ON_OFF:
            self.v1 = config.one_voltage
            self.v0 = 0.0

    def set_source(self, src):
        '''Explicitly set the source for this sender.'''
        self.source = src

    def gain_samples(self):
        return [i * self.v1 for i in self.source.payload]

    def modulated_samples(self):
        '''Returns the modulated signal'''
        samples = self.gain_samples()
        return util.modulate(self.fc, samples, self.sample_rate)

        
