#!/usr/bin/python

'''Defines the Receiver class, which performs the primary receiver
functionality (demodulate + filter + digitize).'''

import math
import numpy
import scipy.cluster.vq
import warnings

class GraphInfo:
    def __init__(self):
        pass

class Receiver:

    def __init__(self, fc, config):
        self.key_type = config.key_type
        self.fc = fc
        self.sample_rate = config.sample_rate
        self.graph_info = None

    def process(self, samples):
        '''The physical-layer receive.  For sending tones, this function
        simply chops off the initial samples of silence (in a pretty crude way).'''

        signal_start = 0
        for i in range(len(samples)):
            if samples[i] > .1:
                signal_start = i
                break

        warnings.filterwarnings('error')
        self.graph_info = GraphInfo() # store some information for graphing
        self.graph_info.received_samples = samples

        return samples[signal_start:]
