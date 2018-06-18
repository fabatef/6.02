#!/usr/bin/python

'''Defines the Source class, which generates a payload given a
particular source type.  In the future, this class will also take care
of sources such as bits, files, images, etc.'''

import random
import sys

class Source:

    ONES = 1

    def __init__(self, config, channel_index):

        self.type = config.src_type
        self.n_samples = config.n_samples

        if self.type == Source.ONES:
            self.payload = [1] * self.n_samples
        
        # For outputting data types
        self._str_map = {Source.ONES : "all ones (long tone)"}

    def __str__(self):
        s = "Data type: %s\n" % (self._str_map[self.type])
        s += "\tData size: %d samples\n" % (self.n_samples)
        return s
