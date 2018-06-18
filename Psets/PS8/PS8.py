import argparse

import dv
import ls
import PS8_tests

from PS8_netsim import RouterNetwork

class DVRouterNetwork(RouterNetwork):
    def make_node(self, loc, address=None):
        return dv.DVRouter(loc, address=address)

class LSRouterNetwork(RouterNetwork):
    def make_node(self, loc, address=None):
        return ls.LSRouter(loc, address=address)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--numnodes", type=int, default=12, help="number of nodes")
    parser.add_argument("-t", "--simtime", type=int, default=2000, help="simulation time")
    parser.add_argument("-r", "--rand", action="store_true", default=False, help="use randomly generated topology")
    parser.add_argument("-p", "--protocol", type=str, default="dv", choices=["dv", "ls"], help="routing protocol (dv or ls)")
    parser.add_argument("-s", "--tests", action="store_true", default=False, help="run tests")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="verbose output")

    args = parser.parse_args()

    if args.tests:
        if args.protocol == "dv":
            PS8_tests.verify_routes(DVRouterNetwork, args.verbose)
        elif args.protocol == "ls":
            PS8_tests.verify_routes(LSRouterNetwork, args.verbose)
    else:
        print("Without wx, GUI testing is unavailable.  You can use the staff tests (with the -s option) or write your own in PS8.py.")
