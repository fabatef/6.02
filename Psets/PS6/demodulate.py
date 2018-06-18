#!/usr/bin/python

'''Defines different demodulators to use in the demodulation step.'''

import math
import numpy

import util

def envelope_demodulator(samples):
    '''Perform envelope demodulation on a set of samples (i.e., rectify
    the samples).

    Arguments:
    samples -- array of samples to demodulate'''
    return numpy.abs(samples)

def heterodyne_demodulator(samples, sample_rate, carrier_freq):
    #do modulation again on the received samples
    n = len(samples)
    omega = (2 * math.pi * carrier_freq)/sample_rate
    return samples * numpy.cos(numpy.arange(0,n)*omega)

def quadrature_demodulator(samples, sample_rate, carrier_freq):

    #fundamental angular frequency
    n = len(samples)
    omega = (2 * math.pi * carrier_freq)/sample_rate

    #In-phase term
    I_n = samples * numpy.cos(numpy.arange(0,n)*omega)

    #Quadrature term
    Q_n = samples * numpy.sin(numpy.arange(0,n)*omega)

    #Returning y[n]= I_n + jQ_n
    output = numpy.array([complex(i,j) for i,j in zip(I_n,Q_n)])
    
    return output
