#!/usr/bin/python

'''Defines main() for Audiocom, which parses arguments and calls
run().  run() sends modulated samples across the channel.  On the
receiving end, the samples are lightly processed to chop off silent
samples (in future labs, they will be more thoroughly processed)'''

import argparse
import numpy
import sys

import graphs
import util

from audio_channel import AudioChannel
from abstract_channel import AbstractChannel
from config import Config
from receiver import Receiver
from sender import Sender
from source import Source

def run(config):

    # Create the sources
    sources = {}
    for i in range(len(config.channels)):
        frequency = config.channels[i]
        source = Source(config, i)
        print("Channel: %d Hz" % frequency)
        print("\n".join(["\t%s" % source]))
        sources[frequency] = source

    # Create a sender for each source, so we can process the bits to
    # get the modulated samples.  We combine all of the modulated
    # samples into a single array by adding them.
    modulated_samples = []
    baseband_samples = []

    for frequency in sources:
        src = sources[frequency]
        sender = Sender(frequency, config)
        sender.set_source(src)

        modulated_samples = util.add_arrays(sender.modulated_samples(), modulated_samples)
        baseband_samples = util.add_arrays(sender.gain_samples(), baseband_samples)

        print("sending %d samples" % len(baseband_samples))

    # Create the channel
    if config.bypass:
        channel = AbstractChannel(config.bypass_noise, config.bypass_h)
    else:
        channel = AudioChannel(config)

    # Transmit and receive data on the channel.  The received samples
    # (samples_rx) have not been processed in any way.
    samples_rx = channel.xmit_and_recv(modulated_samples)
    print('Received', len(samples_rx), 'samples')

    for frequency in config.channels:
        r = Receiver(frequency, config)
        try:
            # Call the main receiver function.  The returned array of bits
            # EXCLUDES the preamble.
            chopped_samples  = r.process(samples_rx)
        except Exception as e:
            print(e)
            sys.exit()

    if config.graphs == "time":
        graphs.plot_samples(baseband_samples, modulated_samples, r.graph_info.received_samples, stems=False)
    elif config.graphs == "freq":
        graphs.plot_sig_spectrum(modulated_samples, r.graph_info.received_samples, title="Received Samples")

    if not config.bypass or (config.bypass and not config.know_h):
        h = util.recover_h(modulated_samples, chopped_samples, n_samples=1000)
    else:
        h = channel.h

    # filter
    h_prime = util.recover_h(h, numpy.array([1]), n_samples=1000)
    if config.graphs == "usr":
        recovered_samples = numpy.convolve(chopped_samples, h_prime)
        graphs.plot_usr(chopped_samples, h, recovered_samples, modulated_samples, stems=False)
    

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    # Source and Sink options
    parser.add_argument("-S", "--src", type=str, default='1', choices=['1', 's'], help="payload (0, 1, step, random)")
    parser.add_argument("-n", "--nsam", type=int, default=1000, help="number of voltage samples")

    # Phy-layer Transmitter and Receiver options
    parser.add_argument("-r", "--samplerate", type=int, default=48000, help="sample rate (Hz)")
    parser.add_argument("-i", "--chunksize", type=int, default=256, help="samples per chunk (transmitter)")
    parser.add_argument("-p", "--prefill", type=int, default=60, help="write buffer prefill (transmitter)")
    parser.add_argument("-c", "--channel", type=int, default=1000, help="lowest carrier frequency (Hz)")
    parser.add_argument("-c2", "--channel2", type=int, help="second carrier frequency (Hz)")
    parser.add_argument("-q", "--silence", type=int, default=80, help="#samples of silence at start of preamble")

    # Modulation options
    parser.add_argument("-o", "--one", type=float, default=1.0, help="voltage level for bit 1")
    parser.add_argument("-z", "--zero", type=float, default=0.0, help="voltage level for bit 0 (ignored unless key type is custom)")

    # AbstractChannel options
    parser.add_argument("-a", "--abstract", action="store_true", help="use bypass channel instead of audio")
    parser.add_argument("-k", "--know", default=False, action="store_true", help="use the known h, not recovered h")
    parser.add_argument("-v", type=float, default=0.00, help="noise variance (for bypass channel)")
    parser.add_argument("-u", "--usr", type=str, default='1', help="unit step & sample response (h)")

    # Miscellaneous
    parser.add_argument("-g", "--graph", type=str, choices=['time', 'freq', 'usr'], help="show graphs")
    parser.add_argument("--verbose", action="store_true", help="verbose debugging")

    args = parser.parse_args()

    config = Config(args)
    print(config) # useful output

    # Go!
    run(config)
