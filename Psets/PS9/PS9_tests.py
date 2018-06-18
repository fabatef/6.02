import argparse
import PS9

def run_network(net):
    net.reset()
    net.step(net.simtime)
    source = net.find_node(0,0)
    sink = net.find_node(len(net.nlist) - 1, 0)
    totaldrop = 0
    for node in net.nlist: totaldrop = totaldrop + node.qdrop 
    totalloss = 0
    for link in net.links: totalloss = totalloss + link.linkloss 
    tput = float(sink.app_seqnum)/(net.time - 1)
    return (tput, totaldrop, totalloss)


def test_stop_wait_no_loss():
    warning_flag = False
    # numhops, simtime, window, qsize, loss, xrate, bottleneck
    net = PS9.make_network(1, 10000, 1, 10, 0.00, 0.00, 1)
    tput, _, _ = run_network(net)
    if (tput < .49 or tput > .51):
        print("Warning: Throughput should be near .5 with parameters -w 1 -n 1; yours was %f" % tput)
        warning_flag = True
    net = PS9.make_network(2, 10000, 1, 10, 0.0, 0.0, 1)
    tput, _, _ = run_network(net)
    if (tput < .24 or tput > .26):
        print("Warning: Throughput should be near .25 with parameters -w 1 -n 2; yours was %f" % tput)
        warning_flag = True

    if not warning_flag:
        print("PASSED: Window-size = 1, loss prob = 0")


def test_stop_wait_loss():
    warning_flag = False
    error_flag = False
    net = PS9.make_network(3, 10000, 1, 10, 0.01, 0.00, 1)
    tput, _, _ = run_network(net)
    if (tput < .01):
        print("ERROR: Throughput was %f with parameters -w 1 -n 3 -l .01; should be near .15" % tput)
        print("       Are you handling retransmissions?")
        error_flag = True
    if (tput < .15 or tput > .16):
        print("Warning: Throughput was %f with parameters -w 1 -n 3 -l .01; should be near .155" % tput)
        print("         Are you setting self.timeout correctly?")
        warning_flag = True
    if not error_flag and not warning_flag:
        print("PASSED: Window-size = 1, loss prob > 0")


def test_sliding_window_no_loss():
    # Basic test; no loss
    net = PS9.make_network(10, 10000, 20, 1000, 0.0, 0.00, 1)
    tput, _, _ = run_network(net)
    if (tput < .99):
        print("ERROR: Throughput was %f with parameters -w 20 -n 10 -l 0; should be almost 1" % tput)
    else:
        print("PASSED: Window-size > 1, loss prob = 0")

def test_sliding_window_loss():
    # Large window test
    net = PS9.make_network(10, 10000, 1000, 2000, 0.001, 0.00, 1)
    tput, _, _ = run_network(net)
    if (tput < .9):
        print("ERROR: Throughput was %f with parameters -w 1000 -n 10 -l .001; should be near .96" % tput)
        print("       Are you retransmitting packets correctly and buffering at the receiver?")
        print("       Are you sending more than one new packet per timeslot? (You should not be)")
    elif (tput < .94):
        print("WARNING: Throughput was %f with parameters -w 1000 -n 10 -l .001; should be near .96" % tput)
        print("       Are you sending more than one new packet per timeslot? (You should not be)")
    else:
        print("PASSED: Window-size > 1, loss prob > 1")

def test_infinite_window():
    net = PS9.make_network(10, 10000, 10, 2000, 0.000, 0.00, 1)
    tput, _, _ = run_network(net)
    if (tput < .49):
        print("ERROR: Throughput was %f with parameters -w 10 -n 10 -l 0; should be near .5" % tput)
    elif (tput > .51):
        print("WARNING: Throughput was %f with parameters -w 10 -n 10 -l 0; should be near .5" % tput)
        print("         Are you sending more packets than the size of the window?")
    else:
        print("PASSED: Window-size > 1, loss prob = 0, under-utilized network")



if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--stop", action='store_true', help="Run stop-and-wait tests")
    parser.add_argument("--slide", action='store_true', help="Run sliding-window tests")
    parser.add_argument("-l", "--loss", action='store_true', help="Allow loss in the network")
    parser.add_argument("-a", "--all", action='store_true', help="Run all tests")

    args = parser.parse_args()

    if args.all:
        args.stop = True
        args.loss = True
        args.slide = True

    if args.stop and not args.slide:
        print("=== Running stop-and-wait tests only ===")
    elif args.slide and not args.stop:
        print("=== Running sliding-window tests only ===")
    elif args.slide and args.stop:
        print("=== Running stop-and-wait and sliding-window tests ===")
    else:
        print("=== Running no tests ===")

    if args.loss:
        print("=== Testing loss on the network ===")
    else:
        print("=== Not testing loss on the network ===")

    if args.stop:
        test_stop_wait_no_loss()
        if args.loss:
            test_stop_wait_loss()
    if args.slide:
        test_sliding_window_no_loss()
        test_infinite_window()
        if args.loss:
            test_sliding_window_loss()


