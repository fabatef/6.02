#!/usr/bin/python

'''Defines different filters to use in the filtering step.'''

import math
import numpy

def averaging_filter(samples, window):
    '''Pass samples through an averaging filter.

    Arguments:
    samples -- samples to average
    window -- window size to use for averaging

    Returns: an array r that is the same size as samples.  r[x] =
    average of samples[x-window] to samples[x], inclusive.  When x <
    window, the averaging window is truncated.
    '''
    x = [0.0]*len(samples)
    for i in range(len(samples)):
        if i-window+1 < 0: # Beginning of the array
            x[i] = numpy.mean(samples[0:i+1])
        else:
            x[i] = numpy.mean(samples[i-window+1:i+1])
    return numpy.array(x)

def low_pass_filter(samples, channel_gap, sample_rate, L=50):
    #omega_cut = half way between the channel gap(delta f_c). (2*pi*delta f_c)/2*sample_rate
    #h[n] = sin(Omega_cut n)/pi*n   (for a gain of 1 on H), h[0] = omega_cut/pi
    #h[0] on this numpy array is h[-L] in samples, so h[L] on this numpy array is h[0] in samples
    numpy.seterr(divide='ignore', invalid = 'ignore')
    omega_cut = (math.pi*channel_gap)/sample_rate
    h = numpy.divide(numpy.sin(omega_cut*numpy.arange(-L, L+1)), math.pi*numpy.arange(-L,L+1))
    h[L] = omega_cut/math.pi #resolving divide by 0
    return numpy.convolve(samples, h)
