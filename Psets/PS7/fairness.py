from PS7 import *
import itertools

def find_fairness():
    p_min = [0.01, 0.02, 0.03]
    p_max = [0.25, 0.35, 0.4, 0.45, 0.55, 0.6, 0.75, 0.8, 0.85, 0.9, 0.95, 1]
    trials = [i for i in itertools.product(p_min, p_max) if i[0] < i[1]]
    for p_min, p_max in trials:
        run = 7
        util = []
        fair = []
        while run != 0:
            wnet = CSMAWirelessNetwork(8, 10, 100, True, 'Mine', False, p_max, p_min, 100000)
            wnet.step(wnet.config.simtime, do_output=False)
            f = wnet.fairness(0)
            u = 1.0*wnet.stats.success*wnet.config.ptime/wnet.time
            util.append(u)
            fair.append(f)
            run -=1
        avg_util = sum(util)/len(util)
        avg_fair = sum(fair)/len(fair)
        if avg_util > 0.7 and all([i>=0.95 for i in fair]):
            print ('P_MIN:', p_min, 'P_MAX:', p_max, 'UTIL:', avg_util, 'FAIR:', avg_fair)
#find_fairness()

def test():
    run = 20
    out = []
    count = 0
    while run != 0:
        wnet = CSMAWirelessNetwork(8, 10, 100, True, 'Mine', False, 0.9, 0.02, 100000)
        wnet.step(wnet.config.simtime, do_output=False)
        f = wnet.fairness(0)
        u = 1.0*wnet.stats.success*wnet.config.ptime/wnet.time
        if u<0.75 or f <0.95:
            count+=1
        out.append((u,f))
        run -=1
    print (out, count)
test()

#5 times in 20 runs (0.01, 0.9)
#


        
