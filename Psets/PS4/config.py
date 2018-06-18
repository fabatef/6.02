#!/usr/bin/python

'''Converts commandline arguments into a configuration.'''

import sys

from source import Source
from sender import Sender
from receiver import Receiver

class Config:

    def __init__(self, args):

        # Convert source type to a valid type
        if args.src == "1":
            self.src_type = Source.ONES
        else:
            sys.stderr.write("Undefined payload type\n")
            sys.exit()

        self.n_samples = args.nsam
        self.sample_rate = args.samplerate
        self.chunk_size = args.chunksize
        self.prefill = args.prefill

        self.lowest_channel = int(args.channel)

        self.channels = [self.lowest_channel]
        if args.channel2 is not None:
            self.channels.append(args.channel2)

        self.n_silent_samples = args.silence
        self.one_voltage = args.one
        self.zero_voltage = args.zero

        # Signaling type
        self.key_type = Sender.ON_OFF

        # AbstractChannel options
        self.bypass = args.abstract
        if self.bypass:
            self.bypass_noise = args.v
            self.know_h = args.know

            if '_' in args.usr:
                self.bypass_h = [float(x) for x in args.usr.split('_')]
            else:
                self.bypass_h = [float(x) for x in args.usr.split(' ')]

        # Graphs + verbosity
        self.graphs = args.graph
        self.verbose = args.verbose

    def __str__(self):
        s = "Parameters in experiment:\n"
        s += "\tKeying scheme: %s\n" % self.key_type
        s += "\tChannel type: %s\n" % ('Audio' if not self.bypass else 'Bypass')
        if self.bypass:
            s += '\t  Noise: %s h: [%s]\n' % (self.bypass_noise, self.bypass_h)
        if len(self.channels) == 1:
            s += "\tFrequency (Hz): %s" % (self.channels[0])
        else:
            s += "\tFrequencies (Hz): %s" % (", ".join([str(x) for x in self.channels]))
        return s
