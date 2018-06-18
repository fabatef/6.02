from PS7_wsim import *
from PS7 import *

class PS7_Tests:
    def __init__(self):
        self.all_tests_passed = True

    def test_collisions(self, wnet):
        for node in wnet.nlist:
            if node.stats.collisions > 0: 
                return False
        return True

    def tdma_tests(self):
        failure = False
        warning = False
        # -t 2000
        wnet = TDMAWirelessNetwork(16, 1, 100, False, False, 2000)
        wnet.step(wnet.config.simtime, do_output=False)
        if not self.test_collisions(wnet):
            print("TDMA: Collision in baseline test (parameters: -t 2000)")
            failure = True

        # -t 14000 -s 7
        wnet = TDMAWirelessNetwork(16, 7, 100, False, False, 14000)
        wnet.step(wnet.config.simtime, do_output=False)
        if not self.test_collisions(wnet):
            print("TDMA: Collision in packet size test (parameters: -t 14000 -s 7)")
            failure = True

        # -n 20 -k
        wnet = TDMAWirelessNetwork(20, 1, 100, False, True, 10000)
        wnet.step(wnet.config.simtime, do_output=False)
        if not self.test_collisions(wnet):
            print("TDMA: Collision in skewed load test (parameters: -n 20 -k)")
            failure = True

        wnet = TDMAWirelessNetwork(16, 1, 100, False, False, 2000)
        wnet.step(wnet.config.simtime, do_output=False)
        f = wnet.fairness(0)
        u = 1.0*wnet.stats.success*wnet.config.ptime/wnet.time

        if u < .9:
            print("Warning: TDMA utilization was %f; expected a value above .9 (parameters were -t 2000)" % u)
            warning = True
        if f < .98:
            print("Warning: TDMA fairness was %f; expected a value near 1 (parameters were -t 2000)" % f)
            warning = True

        if not failure and not warning:
            print("TDMA tests passed")
        elif not failure:
            self.all_tests_passed = False
            print("TDMA is collision-free, but fairness and/or utilization appear low")
            print("== TDMA tests failed ==")
        else:
            self.all_tests_passed = False
            print("== TDMA tests failed ==")


    def aloha_tests(self):
        warning = False
        wnet = AlohaWirelessNetwork(16, 1, 100, True, 'Mine', False, 1, 0, 10000)
        wnet.step(wnet.config.simtime, do_output=False)
        f = wnet.fairness(0)
        u = 1.0*wnet.stats.success*wnet.config.ptime/wnet.time
        if u < .37:
            print("Warning: ALOHA utilization is %f; expected a value above .37 (parameters were -r --pmax=1 --pmin=0 -t 10000)" % u)
            warning = True
        if not warning:
            print("ALOHA tests passed")
        else:
            self.all_tests_passed = False
            print("== ALOHA tests failed ==")


    def csma_tests(self):
        warning = False
        wnet = CSMAWirelessNetwork(8, 10, 100, True, 'Mine', False, 1, 0, 100000)
        wnet.step(wnet.config.simtime, do_output=False)
        f = wnet.fairness(0)
        u = 1.0*wnet.stats.success*wnet.config.ptime/wnet.time
        if u < .7 or u > .8:
            print("Warning: CSMA utilization is %f; expected a value between .7 and .8 (parameters were -r --pmin=0 --pmax=1 -s 10 -t 100000 -n 8)" % u)
            warning = True
        if f < .75 or f > .97:
            print("Warning: CSMA fairness is %f; expected a value between .75 and .97 (parameters were -r --pmin=0 --pmax=1 -s 10 -t 100000 -n 8)" % f)
            warning = True

        if not warning:
            print("CSMA tests passed")
        else: 
            self.all_tests_passed = False
            print("== CSMA tests failed ==")

    def cw_tests(self):
        warning = False
        wnet = CSMACWWirelessNetwork(16, 10, 100, True, False, False, 1, 256, 100000)
        wnet.step(wnet.config.simtime, do_output=False)
        f = wnet.fairness(0)
        u = 1.0*wnet.stats.success*wnet.config.ptime/wnet.time
        if u < .67:
            print("Warning: CSMA/CW utilization is %f; expected a value near .7 (parameters were r -s 10 -n 16 -t 100000 -W 256)" % u)
            warning = True
        if f < .89:
            print("Warning: CSMA/CW fairness is %f; expected a value near .9 (parameters were r -s 10 -n 16 -t 100000 -W 256)" % f)
            warning = True

        if not warning:
            print("CSMA/CW tests passed")
        else:
            self.all_tests_passed = False
            print("== CSMA/CW tests failed ==")


if __name__ == "__main__":
    print("====== Running PS7 tests ======")
    ps7 = PS7_Tests()
    ps7.tdma_tests()
    ps7.aloha_tests()
    ps7.csma_tests()
    ps7.cw_tests()
    if ps7.all_tests_passed:
        print("====== All tests passed! :) ======")
    else:
        print("====== PS7 tests failed ====== ")
