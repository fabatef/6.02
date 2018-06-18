import sys

import numpy
import os
import matplotlib.pyplot as plt

import util

from system import System

class Image(System):

    def __init__(self, noise_level):
        super(Image, self).__init__(noise_level)
        self.filename = None

    # Make sure the image is a valid RGB file (not, e.g., RGBA or
    # grayscale).  If it is, store its dimensions.
    def set_data(self, filename):
        if not os.path.isfile(filename):
            print("Cannot set file: file %s doesn't exist." % filename)
            return

        img = plt.imread(filename)
        if len(img.shape) != 3:
            print("image.py cannot handle non-RGB images")
            sys.exit(-1)

        self.n_rows, self.n_cols, _ = img.shape
        self.filename = filename

    # RGB files are stored as n x m x 3 arrays: n rows, m columns, and
    # 3 float values per pixel (all floats are within [0.0, 1.0].  The
    # three float values are the red, blue, and green values of the
    # pixel.
    #
    # Read in those values, and return them as a one-dimensional list.
    def get_analog_data(self):
        if self.filename is None:
            print("Cannot get data without setting filename")
            sys.exit(-1)
        img = plt.imread(self.filename)
        x = numpy.reshape(img, -1)
        return x

    # Get the analog data and convert that to bits
    def get_digital_data(self):
        floats = self.get_analog_data()
        bits = util.floats_to_bits(floats)
        return bits

    # Write the analog data to a new file, changing the name from
    # file.ext to file_analog.ext.  Writing new data just involves
    # reshaping the array from a 3nm x 1 array to an m x n x 3 array.
    def output_analog(self, data):
        ext = self.filename.split(".")[-1]
        new_filename = self.filename.rstrip("." + ext) + "_analog." + ext
        print("Outputting to file: %s" % new_filename)
        new_data = numpy.reshape(data, (self.n_rows, self.n_cols, 3))
        plt.imsave(new_filename, new_data)

    # Write the digital data to a new file, changing the name from
    # file.ext to file_digital.ext.  Once we convert the bits to
    # floats, the process is the same as it is for analog data.
    def output_digital(self, data):
        ext = self.filename.split(".")[-1]
        new_filename = self.filename.rstrip("." + ext) + "_digital." + ext
        print("Outputting to file: %s" % new_filename)
        floats = util.bits_to_floats(data)
        new_data = numpy.reshape(floats, (self.n_rows, self.n_cols, 3))
        plt.imsave(new_filename, new_data)
