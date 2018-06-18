import math
import numpy
import util
import sys

from receiver import Receiver

class Preamble:
    '''
    This class defines the preamble that appears at the beginning of
    every transmission.  The preamble is comprised of a known bit
    sequence, possibly preappended with some samples of silence.
    '''

    def __init__(self, config):
        '''
        config contains the config options for this system.  Preamble
        gets the number of silent samples, if any, from this.
        '''
        # Preamble bit sequence
        self.data = [1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1] 

        # In practice, some setups require some number of samples of
        # silence before anything is sent (this is a quirk of specific
        # systems for a variety of reasons; it has nothing to do with
        # the theory of LTI systems or anything like that.)
        if config is None:
            self.silence = 0
        else:
            self.silence = config.n_silent_samples
            if config.skip_preamble:
                self.data = []

        # The actual preamble to any message, then, is silence + data.
        self.preamble = numpy.append([0]*self.silence, self.data)

    def preamble_data_len(self):
        '''
        Returns the length of the preamble data bits
        '''
        return len(self.data)

    def detect(self, demodulated_samples, receiver, offset_hint, zero, one):
        '''
        Detects the preamble in an array of demodulated samples.

        Arguments:
        demodulated_samples = numpy.array of demodulated samples

        receiver = Receiver associated with the reception of the
        demodulated samples.  Used to access the samples per bit,
        sample rate, and carrier frequency of this data.

        offset_hint = our best guess as to where the first 1 bit in
        the samples begins

        zero = best guess for V_0 for these samples
        one = best guess for V_1 for these samples

        Returns:
        The index (as an int) into demodulated_samples where the
        preamble is most likely to start.
        '''
        #Get ideal set of preamble samples
        #i.e. convert the preamble bits in self.data to samples, then modulate them
        #then demodulate and filter them.
        preamble_samples = util.bits_to_samples(self.data, receiver.spb, zero, one)
        modulated_preambles = util.modulate(receiver.fc, preamble_samples, receiver.sample_rate)
        demod_filter_preambles = receiver.demodulate_and_filter(modulated_preambles)

        #correlate ideal preamble samples to the demodulated samples sequence
        #and return the preamble start index
        start_indx = offset_hint + self.correlate(demod_filter_preambles, demodulated_samples[offset_hint:])
        return start_indx

    def correlate(self, x, y):
        '''
        Calculate correlation between two arrays.  This function is looking for vector x in vector y.
        
        Arguments:
        x, y: numpy arrays to be correlated

        Returns:
        - If len(x) == 0 or len(x) > len(y), returns 0
        - Else, returns the index into y representing the most-likely
          place where x begins.  "most-likely" is defined using the
          normalized dot product between x and y
        '''

        import warnings
        warnings.filterwarnings("error")
        
        # If x is too long or is nothing, we can't hope to find it.
        # In a real system, we would handle this error more elegantly.
        # For the purposes of your pset, we want the system to exit
        # entirely -- this error indicates a problem with how you're
        # writing detect().
        if len(x) > len(y):
            print("Error in correlate: cannot find x in y if x is longer than y")
            sys.exit(-1)
        if len(x) == 0:
            print("Error in correlate: cannot find x in y if x is of length 0.")
            sys.exit(-1)

        try:
            return numpy.argmax(numpy.correlate(y,x)/numpy.sqrt(numpy.convolve(numpy.ones(len(x)),y**2,mode='valid')))
        except RuntimeWarning: # similarly, we're going to exit entirely on this error
            print("Error: Correlate detected division by zero")
            print("The offset_hint argument to detect() will help avoid this problem.")
            sys.exit()
