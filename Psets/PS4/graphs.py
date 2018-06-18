#!/usr/bin/python

'''Defines functions for making particular plots.'''

import platform
import math
import numpy
import warnings
import matplotlib

if platform.uname()[0] == 'Darwin':
    matplotlib.use('macosx')

import matplotlib.pyplot as p

def get_spec(samples):
    P = len(samples)
    omega1 = 2*math.pi/P
    omegak = omega1*P*numpy.fft.fftfreq(P)
    X = numpy.fft.fft(samples)
    return omegak, X

def plot_sig_spectrum(modulated_samples, demodulated_samples, title="Demodulated Samples"):
    p.figure()

    p.subplot(211)
    omegas, Xs = get_spec(modulated_samples)
    p.plot(omegas, abs(Xs))
    p.title("Modulated Samples")
    p.xlabel("Omega")
    p.xlim((-math.pi, math.pi))

    y_min = min(abs(Xs))
    y_max = max(abs(Xs))

    p.subplot(212)
    omegas, Xs = get_spec(demodulated_samples)
    p.plot(omegas, abs(Xs))
    p.title(title)
    p.xlabel("Omega")
    p.xlim((-math.pi, math.pi))
    p.ylim([y_min, y_max])

    warnings.filterwarnings("ignore")
    p.tight_layout()
    p.show()

def plot_usr(received_samples, h, recovered_samples, original_samples, stems=False):

    p.figure()
    p.subplot(311)
    p.xlabel('Sample number')
    p.ylabel('Voltage')
    p.title('Original (Modulated) Samples, ' + r'$x[n]\cos(\Omega n)$')
    if stems:
        p.stem(range(len(original_samples)), original_samples)
    else:
        p.plot(range(len(original_samples)), original_samples)


    p.subplot(312)
    p.xlabel('Sample number')
    p.ylabel('Voltage')
    p.title('Received Samples, ' + r'$((x\times\cos(\Omega n))*h)[n]$')
    if stems:
        p.stem(range(len(received_samples)), received_samples)
    else:
        p.plot(range(len(received_samples)), received_samples)

    p.subplot(313)
    p.xlabel('Sample number')
    p.ylabel('Voltage')
    p.title('Deconvolved Samples, ' + r"""$(((x\times\cos(\Omega n))*h)*h')[n]$""")
    if stems:
        p.stem(range(len(recovered_samples)), recovered_samples)
    else:
        p.plot(range(len(recovered_samples)), recovered_samples)

    warnings.filterwarnings("ignore")
    p.tight_layout()
    p.show()
    


def plot_samples(baseband_samples, modulated_samples, received_samples, stems=False, spb=None):
    '''Plot an array of samples.

    Arguments:
    samples -- samples to plot
    name -- title for graph
    spb -- samples per bit
    show -- if true, displays the graph (if false, usually there is a
    separate call to p.show() in a later function)
    '''

    p.figure()
    p.subplot(311)

    p.xlabel('Sample number')
    p.ylabel('Voltage')
    p.title('Baseband Samples')
    if stems:
        p.stem(range(len(baseband_samples)), baseband_samples)
    else:
        p.plot(range(len(baseband_samples)), baseband_samples)

    p.subplot(312)
    p.xlabel('Sample number')
    p.ylabel('Voltage')
    p.title('Modulated Samples')
    if stems:
        p.stem(range(len(modulated_samples)), modulated_samples)
    else:
        p.plot(range(len(modulated_samples)), modulated_samples)

    p.subplot(313)
    p.xlabel('Sample number')
    p.ylabel('Voltage')
    p.title('Received Samples')
    if stems:
        p.stem(range(len(received_samples)), received_samples)
    else:
        p.plot(range(len(received_samples)), received_samples)

    warnings.filterwarnings("ignore")
    p.tight_layout()
    p.show()
