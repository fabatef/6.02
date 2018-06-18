import math
import util
import numpy


def test_recover_h():
    '''Does some simple tests for your recover_h function.'''

    # This is the example from class.  The resulting h_prime should be
    # equal to approximately (-.8)^n*u[n].
    x = numpy.array([1, .8])
    y = numpy.array([1])

    h_prime = util.recover_h(x, y, n_samples=40)
    real_h_prime = [(-.8)**n for n in range(0, 40)]

    if not numpy.allclose(h_prime, real_h_prime):
        print("Recover h test 1/3 failed")
        print("Your values for h:", h_prime)
        print("Correct value for h:", real_h_prime)
    else:
        print("Receiver h test 1/3 passed")

    # A second test.  Doubling the input should result in doubling the
    # output, using the same h.
    x = numpy.array([2, 1.6])
    y = numpy.array([2])

    h_prime = util.recover_h(x, y, n_samples=40)

    if not numpy.allclose(h_prime, real_h_prime):
        print("Recover h test 2/3 failed")
        print("Your values for h:", h_prime)
        print("Correct value for h:", real_h_prime)
        print("This test uses an input where x[0] != 1.  Make sure you are using x[0] correctly!")
    else:
        print("Receiver h test 2/3 passed")

    # A third test, with x[0] = 0.  A delay in the input should result
    # in a delay in the output, using the same h.
    x = numpy.array([0, 1, .8])
    y = numpy.array([0, 1])

    h_prime = util.recover_h(x, y, n_samples=40)

    if not numpy.allclose(h_prime, real_h_prime):
        print("Recover h test 3/3 failed")
        print("Your values for h:", h_prime)
        print("Correct value for h:", real_h_prime)
        print("This test uses an input where x[0] = 0 (and so y[0] = 0).  Make sure you are correctly handling an input where the initial samples are 0.0.")
    else:
        print("Receiver h test 3/3 passed")


test_recover_h()
