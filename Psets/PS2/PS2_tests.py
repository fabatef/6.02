import numpy
import random
import sys

import block

def insert_errors(integer_bits, codeword_length, max_errors_per_codeword):

    # Move through codeword-by-codeword
    for i in range(0, len(integer_bits), codeword_length):

        # Insert between 0 and max_errors_per_codeword errors into this word
        num_errors = random.randint(0, max_errors_per_codeword)

        # Randomize the bit indices in this codeword, and flip the
        # first num_errors of them (this is equivalent to randomly
        # selecting num_errors indices without replacement)
        bit_indices = list(range(i, i+codeword_length))
        random.shuffle(bit_indices)

        for j in range(num_errors):
            ix = bit_indices[j] # ix is the index of the bit to flip
            integer_bits[ix] = 1 - integer_bits[ix] # flip it

    # Note: If you'd like to figure out which bits were flipped, you
    # can keep track of the various values for ix, and print that at
    # the end.

    return integer_bits

def test_encode():
    message_bits = numpy.asarray([int(i) for i in "011011111010000001100101101111100000"])

    # Example 1 from page 67
    A = numpy.array([[1, 0, 1, 0, 0], [1, 0, 0, 1, 0], [1, 0, 0, 0, 1], [0, 1, 1, 0, 0], [0, 1, 0, 1, 0], [0, 1, 0, 0, 1]])
    encoder = block.BlockEncoder()
    x = encoder.encode(A, message_bits)

    encoded_bits = numpy.asarray([int(i) for i in "011011000001110101110100000101001100101100011011110101010000010100"])
    if not numpy.array_equal(x, encoded_bits):
        print("Encode incorrect\nA:\n", A, "\nMessage bits:\n", message_bits, "\nYour encoding:\n", x, "\nCorrect encoding:\n", encoded_bits, encoded_bits.shape)
        return False

    # Example 2 from page 67
    A = numpy.array([[1, 1, 0], [1, 0, 1], [0, 1, 1], [1, 1, 1]])
    x = encoder.encode(A, message_bits)

    encoded_bits = numpy.asarray([int(i) for i in "011011011111111010101000000001101100101010101101011100000000000"])
    if not numpy.array_equal(x, encoded_bits):
        print("Encode incorrect\nA:\n", A, "\nMessage bits:\n", message_bits, "\nYour encoding:\n", x, "\nCorrect encoding:\n", encoded_bits, encoded_bits.shape)
        return False
    return True

def test_decode(errors=False):

    # Example 1 from page 67
    message_bits = numpy.asarray([int(i) for i in "011011111010000001100101101111100000"])
    A = numpy.array([[1, 0, 1, 0, 0], [1, 0, 0, 1, 0], [1, 0, 0, 0, 1], [0, 1, 1, 0, 0], [0, 1, 0, 1, 0], [0, 1, 0, 0, 1]])
    encoded_bits = numpy.asarray([int(i) for i in "011011000001110101110100000101001100101100011011110101010000010100"])

    # Insert random errors
    if errors:
        (k, m) = A.shape
        encoded_bits = insert_errors(encoded_bits, k + m, 1)

    decoder = block.SyndromeDecoder()
    x = decoder.decode(A, encoded_bits)

    if not numpy.array_equal(x, message_bits):
        print("Decode incorrect\nA:\n", A, "\nEncoded bits:\n", encoded_bits, "\nYour decoding:\n", x, "\nCorrect decoding:\n", message_bits)
        return False

    # Example 2 from page 67
    A = numpy.array([[1, 1, 0], [1, 0, 1], [0, 1, 1], [1, 1, 1]])
    encoded_bits = numpy.asarray([int(i) for i in "011011011111111010101000000001101100101010101101011100000000000"])

    # Insert random errors
    if errors:
        (k, m) = A.shape
        encoded_bits = insert_errors(encoded_bits, k+m, 1)

    x = decoder.decode(A, encoded_bits)

    if not numpy.array_equal(x, message_bits):
        print("Decode incorrect\nA:\n", A, "\nEncoded bits:\n", encoded_bits, "\nYour decoding:\n", x, "\nCorrect decoding:\n", message_bits)
        return False
    return True
    

def run_all_tests(encode, decode):
    if encode:
        x = test_encode()
        if not x: return
        print("Encode tests passed")
    if decode:
        x = test_decode()
        if not x: return
        for i in range(100):
            x = test_decode(errors=True)
            if not x: return
        print("Decode tests passed")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        run_all_tests(True, True)
    elif sys.argv[1] == "encode":
        run_all_tests(True, False)
    elif sys.argv[1] == "decode":
        run_all_tests(False, True)
    else:
        run_all_tests(True, True)
