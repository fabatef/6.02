import math

'''
This file contains a BitString class, which allows for easier
manipulation of strings of bits (e.g., packing data into a particular
number of bits).
'''

class BitString():

    def __init__(self):
        self.data = []   # packed data
        self.cur_pos = 0 # current bit position

    def __str__(self):
        return str(self.data)

    # The number of bits in the BitString
    def __len__(self):
        return self.cur_pos

    # Input: an integer representing a bit
    #
    # Result: the bit is stored in this BitString (via either an
    # append to self.data or some bit-wise addition on the last bit of
    # self.data)
    def pack_bit(self, bit):
        if bit not in {0, 1}:
            raise ValueError("Bit must be 0 or 1")

        bit_pos = self.cur_pos % 8
        if bit_pos == 0:
            self.data.append(bit)
        else:
            self.data[-1] += (bit << bit_pos)
        self.cur_pos += 1

    # Packs a string of bits via repeated calls to pack_bit.  This is
    # not particularly efficient, but gets the job done.
    def pack_bitstring(self, s):
        for c in s:
            self.pack_bit(int(c))

    # Input:
    #  n, an integer
    #  size, the number of bits to pad n to
    #
    # Result: the number n is stored in this BitString
    def pack_number(self, n, size):
        if type(n) is not int:
            raise ValueError("n must be an integer")
        if n < 0:
            raise ValueError("cannot pack negative numbers")
        if 2**size-1 < n:
            #print (n, size, 2**size-1)
            raise ValueError("size too small for number")

        # Figure out how many bits we need to store the value of n,
        # and how many bits will be left over for padding.
        if n == 0:
            bits_for_n = 1
        else:
            bits_for_n = int(math.log(n, 2)) + 1
        bits_for_padding = size - bits_for_n

        # Store the value + padding.  This could be much faster with a
        # pad_bytes function.
        for i in range(bits_for_padding):
            self.pack_bit(0)
        for i in range(bits_for_n):
            index = bits_for_n - i - 1
            self.pack_bit((n >> index) & 1)

    # Input:
    #  Numbers, a list of integers
    #  size, the number of bits that should represent each integer
    #
    # Result: the list of numbers are stored in this BitString, via
    # repeated calls to pack_number.
    def pack_numbers(self, numbers, size):
        for i in numbers:
            self.pack_number(i, size)

    # Unpacks and returns the most recent bit stored in this
    # BitString.
    def unpack_bit(self):
        bit_pos = (self.cur_pos - 1) % 8
        bit = (self.data[-1] >> bit_pos) & 1
        if bit_pos == 0:
            del self.data[-1]
        self.cur_pos -= 1
        return bit

    # Unpacks and returns the most recent n bits stored in this
    # BitString.
    def unpack_bits(self, n):
        bits = [0] * n
        for i in range(n):
            bits[n-i-1] = self.unpack_bit()
        return bits

    # Unpacks the most recent n bits stored in this BitString, and
    # returns them as a string of 0's and 1's.
    def unpack_bitstring(self, n):
        bits = self.unpack_bits(n)
        return "".join([str(b) for b in bits])

    # Unpacks and returns the integer represented by the most recent
    # n_size bits stored in this BitString.
    def unpack_number(self, n_size):
        bits = self.unpack_bits(n_size)
        m = 0
        for i in range(n_size):
            m += (2**i) * bits[n_size-i-1]
        return m

    # Unpacks and returns all n_size-bit numbers stored in this
    # BitString.  If the length of the data is not divisible by
    # n_size, ignores the extraneous bits.
    def unpack_all_numbers(self, n_size):
        numbers = []
        self.cur_pos -= len(self) % n_size
        while self.cur_pos > 0: # Could be faster
            numbers.insert(0, self.unpack_number(n_size))
        return numbers

    # Writes the data stored in this BitString to a binary file.
    def write_to_file(self, filename):
        with open(filename, 'wb') as outfile:
            for i in range(0, len(self.data), 2):
                elem = bytes(self.data[i:i+2])
                outfile.write(elem)
    
    # Reads the data stored in a binary file, and packs that data into
    # this BitString.  Adjusts self.cur_pos accordingly.
    def read_in_file(self, filename):
#        import array
#        with open(filename, 'rb') as f:
#            encoded = array.array("H", f.read())
        with open(filename, 'rb') as f:
            encoded = f.read()
        for elem in encoded:
            self.data.append(elem)
            self.cur_pos += 8
