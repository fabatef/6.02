import os
import pyaudio
import wave

import util

from system import System

class Sound(System):

    def __init__(self, noise_level):
        super(Sound, self).__init__(noise_level)
        self.filename = None

    # Make sure the given file exists, and open it to get some useful parameters
    def set_data(self, filename):
        if not os.path.isfile(filename):
            print("Cannot set file: file %s doesn't exist." % data)
            return
        self.filename = filename
        with wave.open(self.filename, 'rb') as wf:
            self.n_channels = wf.getnchannels()
            self.frame_rate = wf.getframerate()
            self.sample_width = wf.getsampwidth()
            self.n_frames = wf.getnframes()

    def get_analog_data(self):

        if self.filename is None:
            print("Cannot get data without setting filename")
            sys.exit(-1)

        # Read in the wave file
        CHUNK = 1
        wf = wave.open(self.filename, 'rb')
        data = wf.readframes(CHUNK)

        analog_data = [0.0] * self.n_frames

        # Wave-file data is actually stored as ints in the range
        # [-2**15, 2**15).  These are 16-bit ints stored across two
        # bytes.  We'll shift and scale those values so that we get
        # floats in the range [0.0, 1.0)
        data_index = 0
        while len(data) > 0:
            # Bytes -> ints 
            new_data = bytes([data[0], data[1]])
            x = util.bytes_to_int(data[0], data[1])

            # Ints -> floats
            analog_data[data_index] = float(x + 2**15) / 2**16
            assert(analog_data[data_index] >= 0 and analog_data[data_index] <= 1.0) # double-check

            data = wf.readframes(CHUNK)
            data_index += 1
            
        return analog_data

    # Get the analog data and convert that to bits
    def get_digital_data(self):
        if self.filename is None:
            print("Cannot get data without setting message")
            sys.exit(-1)
        floats = self.get_analog_data()
        bits = util.floats_to_bits(floats)
        return bits

    # Play the wave file, interpreted as analog data.
    def output_analog(self, data):
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(self.sample_width),
                        channels=self.n_channels,
                        rate=self.frame_rate,
                        output=True)

        outfile = []

        # We need to go back from our floats in [0.0, 1.0) to our ints
        # in [-2**15, 2**15).
        for x in data:
            wave_n = int((x * 2**16) - 2**15)
            in_two = util.int_to_bytes(wave_n)
            stream.write(bytes(in_two))
            outfile.append(bytes(in_two))

        stream.stop_stream()
        stream.close()
        p.terminate()

        ext = self.filename.split(".")[-1]
        new_filename = self.filename.rstrip("." + ext) + "_analog." + ext
        print("Outputting to file: %s" % new_filename)
        self.write_wav_file(outfile, new_filename)


    # Play the wave file, interpreted as digital data
    def output_digital(self, data):
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(self.sample_width),
                        channels=self.n_channels,
                        rate=self.frame_rate,
                        output=True)

        outfile = []

        # Take the floats back to two-bit ints in the correct range.
        # Beecause of how floats are formatted and how we've added
        # noise, we occasionally end up with invalid floats; the
        # error-checking below deals with that.
        floats = util.bits_to_floats(data)
        for i in range(len(floats)):

            x = floats[i]

            # Error checking
            try:
                wave_n = int((x * 2**16) - 2**15)
            except:
                wave_n = 0
            if wave_n < -2**15:
                wave_n = -2**15
            elif wave_n >= 2**15:
                wave_n = 2**15 - 1
            
            in_two = util.int_to_bytes(wave_n)
            stream.write(bytes(in_two))
            outfile.append(bytes(in_two))

        stream.stop_stream()
        stream.close()
        p.terminate()

        ext = self.filename.split(".")[-1]
        new_filename = self.filename.rstrip("." + ext) + "_digital." + ext
        print("Outputting to file: %s" % new_filename)
        self.write_wav_file(outfile, new_filename)

    def write_wav_file(self, data, filename):
        wf = wave.open(filename, "wb")
        wf.setnchannels(self.n_channels)
        wf.setsampwidth(self.sample_width)
        wf.setframerate(self.frame_rate)
        wf.setnframes(self.n_frames)
        for b in data:
            wf.writeframesraw(b)
        wf.close()
