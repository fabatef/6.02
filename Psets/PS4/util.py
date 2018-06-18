#!/usr/bin/python

'''Various utility functions, including modulate.'''

import math
import numpy
from numpy import fft
import operator
import sys

def add_arrays(s1, s2):
    '''Adds two numpy arrays together.  If the arrays are of different
    sizes, the sum is performed as if the smaller array were padded
    with 0's at the end.'''
    L = max(len(s1), len(s2))
    a = numpy.append(s1, [0]*(L-len(s1)))
    b = numpy.append(s2, [0]*(L-len(s2)))
    return a + b

def modulate(fc, samples, sample_rate):
    '''Modulate a series of samples using a given frequency and sample rate.'''
    #after mult by the carrier: there are 1/fc samples in one period
    #being sampled at s_r : if the resulting signal needs to have s_r samples
    #in one sec then how many samples are left in one period (1/fc) of the x[n]*carrier
    #signal=> N= s_r *1/fc
    #Omega = 2*pi/N = (2 *pi *fc) / s_r
    #x[n] * cos(Omega n)
    
    n = len(samples)
    omega = (2 * math.pi * fc)/sample_rate
    return samples * numpy.cos(numpy.arange(0,n)*omega)

def recover_h(x, y, n_samples=40):
    '''Recovers h such that x * h = y.'''
    #trim preamble-zeros of the signals then pad the ends with zeros
    no_zeros_x, no_zeros_y  = numpy.trim_zeros(x, 'f'), numpy.trim_zeros(y, 'f')
    #print (n_samples, len(no_zeros_x))
    x = numpy.concatenate((no_zeros_x, numpy.zeros(abs(n_samples - len(no_zeros_x)))))
    y = numpy.concatenate((no_zeros_y, numpy.zeros(abs(n_samples - len(no_zeros_y)))))
    
    #initialize h and n
    h = {}
    h[0] = y[0]/x[0]
    n = 1
    
    #formula that came out of doing the convolution dot product at each n
    while n < n_samples:
        h[n] = (y[n] - sum([h[i]*x[n-i] for i in range(n) if n-i != 0]))/x[0]
        n+=1
    print (h)
    return numpy.array([val for val in h.values()])

