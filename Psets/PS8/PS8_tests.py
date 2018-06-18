# 6.02 routing protocol tests
import os,sys,time,random
from PS8_netsim import *


######################################################################
# Returns true if all routes from source node are correct; False
# otherwise
def verify_route(net, src_node, routing_table, verbose=False):
    src_addr = net.addresses[src_node]

    for dst, expected_routes in routing_table.items():
        route = src_addr.routes.get(dst,None)

        if isinstance(route, Link):
            n = route.end2 if src_addr == route.end1 else route.end1
            route = n.address
        elif route is not None:
            print(route, 'isn\'t a Link; each route should be a Link.')
            return False

        if route not in expected_routes:
            if verbose:
                print('error in routing table: node %s, dst %s, expected %s, got %s' % \
                    (src_node, dst, ' or '.join(expected_routes) if expected_routes[0] is not None else None, route))
            return False
    return True

######################################################################
# Returns true if entire routing table is correct; False otherwise
def verify_routing_table(net, routing_table, verbose=True):
    result = True
    for node in sorted(routing_table.keys()):
        result &= verify_route(net, node, routing_table[node], verbose=verbose)
    return result

######################################################################
# Returns the convergence time of the network as well as whether the
# resulting routing table was correct (we deem a network converged if
# the routing table has been stable for ten time steps)
def calculate_convergence_time(net, correct_routing_table):

    n_stable = 0

    for i in range(100000):
        net.step(count=1)
        result = verify_routing_table(net, correct_routing_table, verbose=False)
        if result:
            n_stable += 1
        else:
            n_stable = 0

        # convergence = ten time steps
        if n_stable == 10:
            break

    return i-9, result

def test0(network, verbose=False):
    '''
    Small Euclidean network, no broken links.  This tests the network
        A---B---C---D
        With link costs = 1

    There are no failures in this network.
    '''

    print('Testing small Euclidean network with no broken links')
    if verbose:
        print('\tA---B---C---D')
        print('\tlink costs = 1')

    NODES =(('A',0,0), ('B',1,0), ('C',2,0), ('D',3,0))
    LINKS = (('A','B'),('B','C'),('C','D'))

    # This is what the final routing table should be
    routing_table = {}
    routing_table['A'] = {'B': ('B',), 'C': ('B',), 'D': ('B',)}
    routing_table['B'] = {'A': ('A',), 'C': ('C',), 'D': ('C',)}
    routing_table['C'] = {'A': ('B',), 'B': ('B',), 'D': ('D',)}
    routing_table['D'] = {'A': ('C',), 'B': ('C',), 'C': ('C',)}

    # Run the simulation
    net = network(4000, NODES, LINKS, 0.0)
    net.reset()
    net.step(count=1000)

    # Verify routes
    result = verify_routing_table(net, routing_table)
    if result:
        print("PASSED")
    else:
        print("FAILED")
    return result

def test1(network, verbose=False):
    '''
    Euclidean network, no broken links.  This tests the network
        A---B   C---D
        |   | / | / |
        E   F---G---H
        With link costs = 1 on straight links, sqrt(2) on diagonal links.

    There are no failures in this network.
    '''

    print('Testing Euclidean network with no broken links')
    if verbose:
        print('\tA---B   C---D')
        print('\t|   | / | / |')
        print('\tE   F---G---H')
        print('\tlink costs = 1 on straight links, sqrt(2) on diagonal links')

    NODES =(('A',0,0), ('B',1,0), ('C',2,0), ('D',3,0),
            ('E',0,1), ('F',1,1), ('G',2,1), ('H',3,1))

    LINKS = (('A','B'),('A','E'),('B','F'),
             ('C','D'),('C','F'),('C','G'),
             ('D','G'),('D','H'),('F','G'),('G','H'))

    # This is what the final routing table should be
    routing_table = {}
    routing_table['A'] = {'B': ('B',), 'C': ('B',), 'D': ('B',), 'E': ('E',), 'F': ('B',), 'G': ('B',), 'H': ('B',)}
    routing_table['B'] = {'A': ('A',), 'C': ('F',), 'D': ('F',), 'E': ('A',), 'F': ('F',), 'G': ('F',), 'H': ('F',)}
    routing_table['C'] = {'A': ('F',), 'B': ('F',), 'D': ('D',), 'E': ('F',), 'F': ('F',), 'G': ('G',), 'H': ('D','G')}
    routing_table['D'] = {'A': ('C','G'), 'B': ('C','G'), 'C': ('C',), 'E': ('C','G'), 'F': ('C','G'), 'G': ('G',), 'H': ('H',)}
    routing_table['E'] = {'A': ('A',), 'B': ('A',), 'C': ('A',), 'D': ('A',), 'F': ('A',), 'G': ('A',), 'H': ('A',)}
    routing_table['F'] = {'A': ('B',), 'B': ('B',), 'C': ('C',), 'D': ('C','G'), 'E': ('B',), 'G': ('G',), 'H': ('G',)}
    routing_table['G'] = {'A': ('F',), 'B': ('F',), 'C': ('C',), 'D': ('D',), 'E': ('F',), 'F': ('F',), 'H': ('H',)}
    routing_table['H'] = {'A': ('G',), 'B': ('G',), 'C': ('D','G'), 'D': ('D',), 'E': ('G',), 'F': ('G',), 'G': ('G',)}

    # Run the simulation
    net = network(4000, NODES, LINKS, 0.0)
    net.reset()
    net.step(count=1000)

    # Verify routes
    result = verify_routing_table(net, routing_table)
    if result:
        print("PASSED")
    else:
        print("FAILED")
    return result

def test2(network, verbose=False):
    ''' This tests a non-Euclidean network; one where the triangle
        inequality does not hold.  The network is:
         A-7-B-1-E
         |     / |
         1  2/   9
         | /     |
         C-4-D-1-F
      
        (link costs are given on their respective links)

        There are no failures.  Typically, if your code passes test1,
        it will pass this test.  If not, make sure you are not making
        any assumptions about the direct link to a neighbor being the
        min-cost path to that neighbor; it may not be.
    '''

    print('Testing non-Euclidean network with no broken links')
    if verbose:
        print('\t A-7-B-1-E')
        print('\t |     / |')
        print('\t 1  2/   9')
        print('\t | /     |')
        print('\t C-4-D-1-F')

    NODES =(('A',0,0), ('B',1,0), ('E',2,0),
            ('C',0,1), ('D',1,1), ('F',2,1))
    LINKS = (('A','B'),('A','C'),('B','C'),
             ('B','D'),('B','E'),('C','D'),
             ('D','F'))

    # We have to explicitly set some costs here
    net = network(4000, NODES, LINKS,0)
    for l in net.links:
        if (l.end1.address == 'A' and l.end2.address == 'B'):
            l.set_cost(7)
        elif (l.end1.address == 'A' and l.end2.address == 'C'):
            l.set_cost(1)
        elif (l.end1.address == 'B' and l.end2.address == 'C'):
            l.set_cost(2)
        elif (l.end1.address == 'B' and l.end2.address == 'D'):
            l.set_cost(9)
        elif (l.end1.address == 'B' and l.end2.address == 'E'):
            l.set_cost(1)
        elif (l.end1.address == 'C' and l.end2.address == 'D'):
            l.set_cost(4)
        elif (l.end1.address == 'D' and l.end2.address == 'F'):
            l.set_cost(1)

    # This is what the correct routing table should be
    routing_table = {}
    routing_table['A'] = {'B': ('C',), 'C': ('C',), 'D': ('C',), 'E': ('C',), 'F': ('C',)}
    routing_table['B'] = {'A': ('C',), 'C': ('C',), 'D': ('C',), 'E': ('E',), 'F': ('C',)}
    routing_table['C'] = {'A': ('A',), 'B': ('B',), 'D': ('D',), 'E': ('B',), 'F': ('D',)}
    routing_table['D'] = {'A': ('C',), 'B': ('C',), 'C': ('C',), 'E': ('C',), 'F': ('F',)}
    routing_table['E'] = {'A': ('B',), 'B': ('B',), 'C': ('B',), 'D': ('B',), 'F': ('B',)}
    routing_table['F'] = {'A': ('D',), 'B': ('D',), 'C': ('D',), 'D': ('D',), 'E': ('D',)}

    # Run the simulation
    net.reset()
    net.step(count=1000)

    # Verify routes
    result = verify_routing_table(net, routing_table)
    if result:
        print('PASSED')
    else:
        print('FAILED')
    return result

def test3(network, verbose=False):
    ''' This tests the same network as in test1, but with a broken link
        between F and G.  The first thing to be sure of here is that
        your route from F to G does indeed change.'''

    print('Testing network with one broken link')
    if verbose:
        print('Breaking F-G link in topology')
        print('\tA---B   C---D')
        print('\t|   | / | / |')
        print('\tE   F-X-G---H')
        print('\tlink costs = 1 on straight links, sqrt(2) on diagonal links')

    NODES =(('A',0,0), ('B',1,0), ('C',2,0), ('D',3,0),
            ('E',0,1), ('F',1,1), ('G',2,1), ('H',3,1))
    LINKS = (('A','B'),('A','E'),('B','F'),
             ('C','D'),('C','F'),('C','G'),
             ('D','G'),('D','H'),('F','G'),('G','H'))

    # Run the simulation for a bit
    net = network(4000, NODES, LINKS, 0.0)
    net.reset()
    net.step(count=1000)

    # break F<-->G link
    for link in net.links:
        if link.end1.address=='F' and link.end2.address=='G':
            link.broken = True
    
    # Keep going, make sure the table repairs itself
    net.step(count=1000)

    # Correct routing table (after link breaking).  Because of ties in
    # min-cost paths, some nodes may have multiple valid routes.  This
    # table lists those options because of how our testing function
    # works, but your routing table should only have a single route
    # for each destination.
    routing_table = {}
    routing_table['A'] = {'B': ('B',), 'C': ('B',), 'D': ('B',), 'E': ('E',), 'F': ('B',), 'G': ('B',), 'H': ('B',)}
    routing_table['B'] = {'A': ('A',), 'C': ('F',), 'D': ('F',), 'E': ('A',), 'F': ('F',), 'G': ('F',), 'H': ('F',)}
    routing_table['C'] = {'A': ('F',), 'B': ('F',), 'D': ('D',), 'E': ('F',), 'F': ('F',), 'G': ('G',), 'H': ('D','G')}
    routing_table['D'] = {'A': ('C',), 'B': ('C',), 'C': ('C',), 'E': ('C',), 'F': ('C',), 'G': ('G',), 'H': ('H',)}
    routing_table['E'] = {'A': ('A',), 'B': ('A',), 'C': ('A',), 'D': ('A',), 'F': ('A',), 'G': ('A',), 'H': ('A',)}
    routing_table['F'] = {'A': ('B',), 'B': ('B',), 'C': ('C',), 'D': ('C',), 'E': ('B',), 'G': ('C',), 'H': ('C',)}
    routing_table['G'] = {'A': ('C',), 'B': ('C',), 'C': ('C',), 'D': ('D',), 'E': ('C',), 'F': ('C',), 'H': ('H',)}
    routing_table['H'] = {'A': ('D','G',), 'B': ('D','G'), 'C': ('D','G'), 'D': ('D',), 'E': ('D','G',), 'F': ('D','G',), 'G': ('G',)}

    result = verify_routing_table(net, routing_table)
    if result:
        print('PASSED')
    else:
        print('FAILED')
    return result

def test4(network, verbose=False):
    ''' This network starts out with a broken link:

         A---B-4-C---D
         |   | /2X /2|
         E---F---G---H
        
        Costs: BC=4 DG=2 CF=2 CG broken; all other costs are 1
    '''

    print('Testing network with broken links')
    if verbose:
        print('\tA---B-4-C---D')
        print('\t|   | /2X /2|')
        print('\tE---F---G---H')
        print('\tCosts: BC=4 DG=2 CF=2 CG broken; all other costs are 1')

    NODES =(('A',0,0), ('B',1,0), ('C',2,0), ('D',3,0),
            ('E',0,1), ('F',1,1), ('G',2,1), ('H',3,1))
    LINKS = (('A','B'),('A','E'),('B','F'),
             ('B','C'),('C','F'),('C','D'),
             ('D','G'),('D','H'),('E','F'),
             ('F','G'),('G','H'),('C','G')) # this last link is going to start out broken

    net = network(4000, NODES, LINKS,0)

    # every other link has cost 1
    for l in net.links:
        if (l.end1.address == 'B' and l.end2.address == 'C'):
            l.cost = 4
        elif (l.end1.address == 'D' and l.end2.address == 'G'):
            l.cost = 2
        elif (l.end1.address == 'C' and l.end2.address == 'F'):
            l.cost = 2
        elif (l.end1.address == 'C' and l.end2.address == 'G'):
            l.broken = True

    net.reset()
    net.step(count=1000)

    # Correct routing table (again, some nodes have multiple possible min-cost paths).
    routing_table = {}
    routing_table['A'] = {'B': ('B',), 'C': ('B','E'), 'D': ('B','E'), 'E': ('B','E',), 'F': ('B','E'), 'G': ('B','E'), 'H': ('B','E')}
    routing_table['B'] = {'A': ('A',), 'C': ('F',), 'D': ('F',), 'E': ('A','F',), 'F': ('F',), 'G': ('F',), 'H': ('F',)}
    routing_table['C'] = {'A': ('F',), 'B': ('F',), 'D': ('D',), 'E': ('F',), 'F': ('F',), 'G': ('D','F'), 'H': ('D',)}
    routing_table['D'] = {'A': ('C','G','H'), 'B': ('C','G','H'), 'C': ('C',), 'E': ('C','G','H'), 'F': ('C','G','H'), 'G': ('G','H'), 'H': ('H',)}
    routing_table['E'] = {'A': ('A',), 'B': ('A','F'), 'C': ('F',), 'D': ('F',), 'F': ('F',), 'G': ('F',), 'H': ('F',)}
    routing_table['F'] = {'A': ('B','E'), 'B': ('B',), 'C': ('C',), 'D': ('C','G','H'), 'E': ('E',), 'G': ('G',), 'H': ('G',)}
    routing_table['G'] = {'A': ('F',), 'B': ('F',), 'C': ('D','F','H'), 'D': ('D','H'), 'E': ('F',), 'F': ('F',), 'H': ('H',)}
    routing_table['H'] = {'A': ('G',), 'B': ('G',), 'C': ('D',), 'D': ('D',), 'E': ('G',), 'F': ('G',), 'G': ('G',)}

    result = verify_routing_table(net, routing_table)
    if result:
        print('PASSED')
    else:
        print('FAILED')
    return result

def test5(network, verbose=False):
    '''This tests the network from test4, breaks a new link, and change
       some costs.  Links CF, CG, and DG get broken, and the costs of BF and
       CD change.'''

    print('Testing network with changing costs and more failures')
    if verbose:
        print('\tA---B-4-C---D')
        print('\t|   | /2X /2|')
        print('\tE---F---G---H')
        print('\tCosts: BC=4 DG=2 CF=2 CG broken; all other costs are 1')
        print()
        print('\tNow breaking CF, CG, DG; changing BF<--15, CD <--13')

    NODES =(('A',0,0), ('B',1,0), ('C',2,0), ('D',3,0),
            ('E',0,1), ('F',1,1), ('G',2,1), ('H',3,1))
    LINKS = (('A','B'),('A','E'),('B','F'),
             ('B','C'),('C','F'),('C','D'),
             ('D','G'),('D','H'),('E','F'),
             ('F','G'),('G','H'),('C','G')) # this last link is going to start out broken

    net = network(4000, NODES, LINKS,0)

    # every other link has cost 1
    for l in net.links:
        if (l.end1.address == 'B' and l.end2.address == 'C'):
            l.cost = 4
        elif (l.end1.address == 'D' and l.end2.address == 'G'):
            l.cost = 2
        elif (l.end1.address == 'C' and l.end2.address == 'F'):
            l.cost = 2
        elif (l.end1.address == 'C' and l.end2.address == 'G'):
            l.broken = True

    # Run before breaking
    net.reset()
    net.step(count=1000)

    # Break, change costs
    for l in net.links:
        if (l.end1.address == 'C' and l.end2.address == 'F'):
            l.broken = True
        elif (l.end1.address == 'B' and l.end2.address == 'F'):
            l.cost = 15
        elif (l.end1.address == 'C' and l.end2.address == 'G'):
            l.broken = False # cost is 1, so this is fine
        elif (l.end1.address == 'C' and l.end2.address == 'D'):
            l.cost = 13
        elif (l.end1.address == 'D' and l.end2.address == 'G'):
            l.broken = True
    
    # Run after breaking; table should repair itself.
    net.step(count=1000)

    routing_table = {}
    routing_table['A'] = {'B': ('B',), 'C': ('E',), 'D': ('E',), 'E': ('E',), 'F': ('E',), 'G': ('E',), 'H': ('E',)}
    routing_table['B'] = {'A': ('A',), 'C': ('C',), 'D': ('A',), 'E': ('A',), 'F': ('A',), 'G': ('A',), 'H': ('A',)}
    routing_table['C'] = {'A': ('G',), 'B': ('B',), 'D': ('G',), 'E': ('G',), 'F': ('G',), 'G': ('G',), 'H': ('G',)}
    routing_table['D'] = {'A': ('H',), 'B': ('H',), 'C': ('H',), 'E': ('H',), 'F': ('H',), 'G': ('H',), 'H': ('H',)}
    routing_table['E'] = {'A': ('A',), 'B': ('A',), 'C': ('F',), 'D': ('F',), 'F': ('F',), 'G': ('F',), 'H': ('F',)}
    routing_table['F'] = {'A': ('E',), 'B': ('E',), 'C': ('G',), 'D': ('G',), 'E': ('E',), 'G': ('G',), 'H': ('G',)}
    routing_table['G'] = {'A': ('F',), 'B': ('F',), 'C': ('C',), 'D': ('H',), 'E': ('F',), 'F': ('F',), 'H': ('H',)}
    routing_table['H'] = {'A': ('G',), 'B': ('G',), 'C': ('G',), 'D': ('D',), 'E': ('G',), 'F': ('G',), 'G': ('G',)}

    result = verify_routing_table(net, routing_table)
    if result:
        print('PASSED')
    else:
        print('FAILED')
    return result

def test6(network, verbose=False):
    ''' This network has two broken links, which results in a disconnected
        network.  It's the same as the default network from test1, but with
        links FC and FG broken (so the network is partitioned into two pieces.

        This should result in routing tables with many 'None' routes.'''

    print('Testing network with two broken links (disconnected network)')
    if verbose:
        print('Breaking links F-C and F-G')
        print('\tA---B   C---D')
        print('\t|   | X | / |')
        print('\tE   F-X-G---H')
        print('\tlink costs = distance (1 or sqrt(2))')

    NODES =(('A',0,0), ('B',1,0), ('C',2,0), ('D',3,0),
            ('E',0,1), ('F',1,1), ('G',2,1), ('H',3,1))
    LINKS = (('A','B'),('A','E'),('B','F'),
             ('C','D'),('C','F'),('C','G'),
             ('D','G'),('D','H'),('F','G'),('G','H'))

    net = network(4000, NODES, LINKS, 0.0)

    for link in net.links:
        # break F<-->C link
        if link.end1.address=='C' and link.end2.address=='F':
            link.broken = True
        # break F<-->G link
        if link.end1.address=='F' and link.end2.address=='G':
            link.broken = True

    net.reset()
    net.step(count=10000)

    # The correct routing table has many 'None' routes, because the network has become disconnected
    routing_table = {}
    routing_table['A'] = {'B': ('B',), 'C': (None,), 'D': (None,), 'E': ('E',), 'F': ('B',), 'G': (None,), 'H': (None,)}
    routing_table['B'] = {'A': ('A',), 'C': (None,), 'D': (None,), 'E': ('A',), 'F': ('F',), 'G': (None,), 'H': (None,)}
    routing_table['C'] = {'A': (None,), 'B': (None,), 'D': ('D',), 'E': (None,), 'F': (None,), 'G': ('G',), 'H': ('D','G')}
    routing_table['D'] = {'A': (None,), 'B': (None,), 'C': ('C',), 'E': (None,), 'F': (None,), 'G': ('G',), 'H': ('H',)}
    routing_table['E'] = {'A': ('A',), 'B': ('A',), 'C': (None,), 'D': (None,), 'F': ('A',), 'G': (None,), 'H': (None,)}
    routing_table['F'] = {'A': ('B',), 'B': ('B',), 'C': (None,), 'D': (None,), 'E': ('B',), 'G': (None,), 'H': (None,)}
    routing_table['G'] = {'A': (None,), 'B': (None,), 'C': ('C',), 'D': ('D',), 'E': (None,), 'F': (None,), 'H': ('H',)}
    routing_table['H'] = {'A': (None,), 'B': (None,), 'C': ('D','G'), 'D': ('D',), 'E': (None,), 'F': (None,), 'G': ('G',)}

    result = verify_routing_table(net, routing_table)
    if result:
        print('PASSED')
    else:
        print('FAILED')
    return result

######################################################################
# Test convergence time
def convergence_test(network, verbose=False):
    '''This test is a little different.  It tests a very basic network,
       changes a cost, and measures how long it takes your routing
       protocol to converge.  If your protocol takes too long, that
       indicates that you have some inefficiencies in how you send or
       integrate advertisements.'''

    print("Testing convergence time on a simple network")
    if verbose:
        print('\t  Y')
        print('\t / \\')
        print('\tX---Z')
        print('\tCosts: XY=4 YZ=1 ZX=12')

    NODES =(('X',0,1), ('Y',1,0), ('Z',2,1))
    LINKS = (('X','Y'),('Y','Z'),('X','Z'))
    net = network(4000, NODES, LINKS,0)

    for l in net.links:
        if (l.end1.address == 'X' and l.end2.address == 'Y'):
            l.cost = 4
        elif (l.end1.address == 'Y' and l.end2.address == 'Z'):
            l.cost = 1
        elif (l.end1.address == 'X' and l.end2.address == 'Z'):
            l.cost = 12

    # this is the correct routing table for the original network
    original_routing_table = {}
    original_routing_table['X'] = {'Y': ('Y',), 'Z': ('Y',)}
    original_routing_table['Y'] = {'X': ('X',), 'Z': ('Z',)}
    original_routing_table['Z'] = {'X': ('Y',), 'Y': ('Y',)}

    # this is the correct table for *both* of the augmented networks
    augmented_routing_table = {}
    augmented_routing_table['X'] = {'Y': ('Z',), 'Z': ('Z',)}
    augmented_routing_table['Y'] = {'X': ('Z',), 'Z': ('Z',)}
    augmented_routing_table['Z'] = {'X': ('X',), 'Y': ('Y',)}

    net.reset()
    net.step(count = 1000)

    # make sure they get the original routing table correct.  we don't care about convergence time yet
    result = verify_routing_table(net, original_routing_table)
    if not result:
        print("FAILED: Error in original routing table")
        return result

    # now change the cost from X -> Z to 2.  routing table should change
    for l in net.links:
        if (l.end1.address == 'X' and l.end2.address == 'Z'):
            l.cost = 2

    c_time, result = calculate_convergence_time(net, augmented_routing_table)
    if not result:
        verify_routing_table(net, augmented_routing_table)
        print("FAILED: Error in first augmented routing table")
        return result

    had_warning=False
    if (c_time > 90):
        print("WARNING: First routing table change took too long to converge (your time was %d; should be below 90)" % c_time)
        had_warning = True

    # reset the network back to the original; again, don't care about this convergence time
    for l in net.links:
        if (l.end1.address == 'X' and l.end2.address == 'Z'):
            l.cost = 12
    net.step(1000)
    result = verify_routing_table(net, original_routing_table)
    if not result:
        print("FAILED: Error in resetting network")
        return result

    # change cost of X -> Y to 14.  routing table should change
    for l in net.links:
        if (l.end1.address == 'X' and l.end2.address == 'Y'):
            l.cost = 14

    # second convergence time.  should be ~390
    c_time, result = calculate_convergence_time(net, augmented_routing_table)
    if result:
        if (c_time > 450):
            print("WARNING: Second routing table change took too long to converge (your time was %d; should be below 450)" % c_time)
            had_warning = True
    else:
        verify_routing_table(net, augmented_routing_table)
        print("FAILED: Error in second augmented routing table")
        return result

    if had_warning:
        print("PASSED, but with warnings")
    else:
        print("PASSED")
    return result


def verify_routes(network, verbose):
    # Each of these tests uses a different type of network.  They go
    # roughly from the easiest to pass to the most difficult to pass.
    # Take a look at each test function for more details.
    results = set()
    results.add(test0(network, verbose=verbose))
    results.add(test1(network, verbose=verbose))
    results.add(test2(network, verbose=verbose))
    results.add(test3(network, verbose=verbose))
    results.add(test4(network, verbose=verbose))
    results.add(test5(network, verbose=verbose))
    results.add(test6(network, verbose=verbose))

    results.add(convergence_test(network, verbose=verbose))

    if False in results:
        print("")
        print("Failed one or more tests")
    else:
        print("")
        print("Passed all tests")
