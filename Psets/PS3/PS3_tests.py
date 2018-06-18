import numpy
import random
import sys
import viterbi

def decode(voltages, G):
    decoder = viterbi.ViterbiDecoder(G)
    return decoder.decode(voltages)


def test_encode(G, message, result):
    encoded = viterbi.ConvolutionalEncoder(G).encode(message)
    test_passed = numpy.all(encoded == result)
    result = "PASSED" if test_passed else "FAILED"
    print("  %s encoding test with message = %s" % (result, message))
    return test_passed

def run_encode_tests():
    G = numpy.array([[1, 1, 1], [1, 0, 1], [0, 1, 1]])
    print("Testing encoding, G =", str(G.tolist()))
    n_tests_passed = 0

    n_tests_passed += 1*test_encode(G, [1, 1, 1], [1, 1, 0, 0, 1, 1, 1, 0, 0])
    n_tests_passed += 1*test_encode(G, [1, 0, 1], [1, 1, 0, 1, 0, 1, 0, 0, 1])

    print("Passed %d out of 2 encoding tests" % n_tests_passed)

    if n_tests_passed != 2:
        print("NOTE: If your encoder is not working, results from the decoding tests will not be accurate")
    print()

def test_decode(G):
    for i in range(100):
        message = numpy.random.random_integers(0, 1, 10)
        voltages = viterbi.ConvolutionalEncoder(G).encode(message)
        decoded_message = decode(voltages, G)
        if numpy.any(message != decoded_message):
            print("  FAILED decoding test with message = %s" % message)
            print("     Decoded message was %s" % decoded_message)
            return False

    print("  PASSED")
    return True

def run_decode_tests():
    n_tests_passed = 0
    G = numpy.array([[1, 1, 1], [1, 0, 1], [0, 1, 1]])
    print("Testing hard-decision decoding with no errors, G =", str(G.tolist()))
    n_tests_passed += 1*test_decode(G)

    G = numpy.array([[1, 1, 1], [1, 1, 0]])
    print("Testing hard-decision decoding with no errors, G =", str(G.tolist()))
    n_tests_passed += 1*test_decode(G)
    print("Passed %d out of 2 decoding tests (no errors introduced into the stream)" % n_tests_passed)
    print()


def test_decode_with_errors(G):
    for i in range(100):
        message = numpy.random.random_integers(0, 1, 10)
        voltages = viterbi.ConvolutionalEncoder(G).encode(message)
        # Make sure the errors are spaced far apart, and not too close
        # to the end of the message.
        err1 = random.randint(0, 4)
        err2 = random.randint(11, 15)
        voltages[err1] = 1 - voltages[err1]
        voltages[err2] = 1 - voltages[err2]
        decoded_message = decode(voltages, G)
        if numpy.any(message != decoded_message):
            print("  FAILED decoding test with message = %s" % message)
            print("     Decoded message was %s" % decoded_message)
            return False

    print("  PASSED")
    return True

def run_error_tests():
    G = numpy.array([[1, 1, 1], [1, 1, 0]])
    print("Testing hard-decision decoding with errors, G =", str(G.tolist()))
    n_tests_passed = 0
    n_tests_passed += 1*test_decode_with_errors(G)
    print("Passed %d out of 1 decoding tests (errors introduced into the stream)" % n_tests_passed)
    print()

def test_soft():
    G = numpy.array([[1, 1, 1], [1, 1, 0]])
    print("Testing soft-decision decoding, G =", str(G.tolist()))
    for i in range(10):
        expected = numpy.random.random_integers(0,1,len(G))
        received = numpy.random.rand(len(G))
        decoder = viterbi.ViterbiDecoder(G)
        dist = decoder.branch_metric(expected, received, soft_decoding=True)
        expected_dist = sum([(expected[j] - received[j])**2 for j in range(len(G))])
        if numpy.any((dist - expected_dist) > 1e-5):
            print("  FAILED")
            print("  Expected voltages:", expected)
            print("  Received voltages:", received)
            print("  Value returned by branch_metric:", dist)
            print("  Expected return value:",expected_dist)
            sys.exit(-1)
    print("  PASSED")

if __name__ == "__main__":
    run_encode_tests() # Encoding tests
    run_decode_tests() # Decoding tests
    run_error_tests()  # More decoding tests
    test_soft() # Uncomment this out to test soft-decision decoding
