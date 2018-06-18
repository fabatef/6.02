from noise import Noise

# Defines a communication system that simulates transmitting data over
# a noisy channel.  The source for the data can be digital or analog.
class System():

    # Initialize the system.  The larger the noise_level, the "louder"
    # the noise.
    def __init__(self, noise_level):
        self.noise_level = noise_level

    # Set the data.  Text, image, sound, etc.
    def set_data(self, data):
        raise NotImplementedError

    # Transmit data over a noisy channel.
    def transmit(self, data):
        noise_values = Noise(self.noise_level).get_noises(len(data))
        noisy_data = data[:]

        for i in range(len(noisy_data)):
            n = noisy_data[i] + noise_values[i]
            # Keep voltage levels within [0.0, 1.0]
            if n >= 1.0:
                n = .999999999
            elif n < 0.0:
                n = 0.0
            noisy_data[i] = n
            assert(noisy_data[i] >= 0.0 and noisy_data[i] <= 1.0) # double-check

        return noisy_data

    # Turns a float value into a 0 or a 1
    def digitize(self, data):
        return [0 if d < .5 else 1 for d in data]

    # Gets the analog data associated with this system.  Involves
    # things like reading from a sound file, reading an image,
    # etc. (depends on the System type).
    def get_analog_data(self):
        raise NotImplementedError

    # Gets the digital data associated with this system.  Involves
    # things like reading from a sound file, reading an image,
    # etc. (depends on the System type).
    #
    # In the current code, this method is virtually the same for every
    # system: get the analog data (as floats), and use the underlying
    # bit representation of those numbers as the digital data.
    #
    # In theory, though, one might use different approaches for
    # different System, much like getting the analog data requires
    # different approaches depending on the data we're dealing with.
    def get_digital_data(self):
        raise NotImplementedError

    # Output a stream of analog data related to this System.  The
    # output might be playing a sound file, saving an image, or
    # printing text.
    def output_analog(self, data):
        raise NotImplementedError

    # Same as above, but for digital data.
    def output_digital(self, data):
        raise NotImplementedError
