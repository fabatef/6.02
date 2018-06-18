#!/usr/bin/python

import numpy

class Noise():

    # Initializes the noise distribution.  The larger sigma is, the
    # "larger" the noise will be.
    def __init__(self, sigma):
        # 0-centered gaussian
        self.sigma = sigma
        
    # Returns a list of n, randomly-generated noise values.
    def get_noises(self, n):
        if self.sigma == 0.0:
            return [0.0] * n
        return numpy.random.normal(0.0, self.sigma, n)
