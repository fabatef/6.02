import struct

# Converts a two's-complement number stored across two bytes into a
# single integer.
def bytes_to_int(byte1, byte2):
    # If the first bit of byte1 is 0, we just have a regular positive
    # number.
    if byte1 < 2**7:
        n = byte1*(2**8) + byte2
    else:
        n = (byte1 - 2**7)*(2**8) + byte2 - 2**15

    assert(n >= -2**15 and n < 2**15) # double-check
    return n

# Converts an integer to a two's complement number stored across two
# bytes (here, the two bytes are actually represented as two
# integers).  As such, the input must be in the range [-2^15, 2^15).
def int_to_bytes(n):

    assert(n >= -2**15 and n < 2**15)

    # Positive numbers are easy
    if n >= 0:
        byte2 = n % (2**8)
        if n < 2**8:
            byte1 = 0
        else:
            byte1 = int((n - byte2)/2**8)
    else:
        y = n + 2**15 # make the number positive
        byte2 = y % (2**8)
        if y < 2**8:
            byte1 = 2**7
        else:
            byte1 = 2**7 + int((y-byte2)/2**8)

    assert(byte1 >= 0 and byte1 < 2**8) # double-check
    assert(byte2 >= 0 and byte2 < 2**8)

    return byte1, byte2

def float_to_bits(f, float_size=32):
    s = [int(x) for x in ''.join([bin(c).replace('0b', '').rjust(8, '0') for c in struct.pack('!f', f)])]
    return s


def floats_to_bits(floats):
    float_size = 32
    digital_data = [0] * len(floats)*float_size
    data_index = 0
    for f in floats:
        digital_data[data_index:data_index + float_size] = float_to_bits(f, float_size=float_size)
        data_index += float_size
    return digital_data


def bits_to_floats(bit_stream):
    float_size = 32
    floats = [0.0] * int(len(bit_stream) / float_size)
    float_index = 0
    for data_index in range(0, len(bit_stream), float_size):
        slice = bit_stream[data_index:data_index + float_size]
        bitstring = ''.join([str(x) for x in slice])
        c_string = [int(bitstring[i:i + 8], 2) for i in range(0, len(bitstring), 8)]
        c_string = bytes(c_string)

        x = struct.unpack('!f', c_string)[0]
        floats[float_index] = x
        float_index += 1
    return floats



