import random,sys,math
from optparse import OptionParser
from PS8_netsim import *
import PS8_tests
import heapq

# Students -- Do not be alarmed by the number of functions in this
# file.  You only need to modify two of them.

class LSRouter(Router):
    INFINITY = sys.maxsize

    def __init__(self,location,address=None):
        # Do not change this function.  You don't need to modify it.
        Router.__init__(self, location, address=address)
        self.LSA = {}
        self.LSA_seqnum = 0

    def send_lsa(self, time):
        # Do not change this function.  You don't need to modify it.
        self.LSA_seqnum += 1
        lsa_info = self.make_ls_advertisement()
        for link in self.links:
            p = self.network.make_packet(self.address, self.peer(link),  'ADVERT', time, color='red', seqnum=self.LSA_seqnum, neighbors=lsa_info)
            link.send(self, p)

    def send_advertisement(self, time):
        # Do not change this function.  You don't need to modify it.
        self.send_lsa(time)
        self.clear_stale_lsa(time)

    def clear_stale_lsa(self, time):
        # Do not change this function.  You don't need to modify it.
        for key,value in self.LSA.items():
            if value[0] < self.LSA_seqnum-1:
                del self.LSA[key]

    def process_advertisement(self, p, link, time):
        # Do not change this function.  You don't need to modify it.
        seq = p.properties['seqnum']
        saved = self.LSA.get(p.source, (-1,))
        if seq > saved[0]:
            if p.properties['neighbors'] is not None:
                self.LSA[p.source] = [seq] + p.properties['neighbors']
            else:
                print(p.properties)
                print('Malformed LSA: No LSA neighbor information in packet.  Exiting...')
                sys.exit(1)
            for link in self.links:
                link.send(self, self.network.duplicate_packet(p))

    def get_all_nodes(self):
        # Do not change this function.  You don't need to modify it.
        nodes = [self.address]
        for u in nodes:
            if self.LSA.get(u) != None:
                lsa_info = self.LSA[u][1:]
                for i in range(len(lsa_info)):
                    v = lsa_info[i][0]
                    if not v in nodes:
                        nodes.append(v)
        return nodes

    def transmit(self, time):
        # Do not change this function.  You don't need to modify it.
        Router.transmit(self, time)
        if (time % self.ADVERT_INTERVAL) == self.ADVERT_INTERVAL/2:
            self.integrate(time)

    def OnClick(self,which):
        # Do not change this function.  You don't need to modify it.
        if which == 'left':
            print(self)
            print('  LSA:')
            for (key,value) in self.LSA.items():
                print('    ',key,': ',value)
        Router.OnClick(self,which)

    def integrate(self, time):
        # Do not change this function.  You don't need to modify
        # it. (the real work is done in run_dijkstra, which you *do*
        # need to modify)
        self.routes.clear()
        self.routes[self.address] = 'Self'
        self.LSA[self.address] = [self.LSA_seqnum] + self.make_ls_advertisement()
        nodes = self.get_all_nodes()
        self.cost_table = {}
        for u in nodes:
            self.cost_table[u] = self.INFINITY
        self.cost_table[self.address] = 0 # path cost to myself is 0
        self.run_dijkstra(nodes)

    def make_ls_advertisement(self):
        # TODO: Your code here.
        #
        # Should return a list of the form [(dest1, cost1), (dest2,
        # cost2) ...].  The variable self.neighbors will be helpful.

        #self.neighbors: a dictionary mapping a Link to a (timestamp, address, linkcost) tuple
        return [(nbr, lnk_cost) for t, nbr, lnk_cost in self.neighbors.values()]
    
    def run_dijkstra(self, nodes):
        # TODO: Your code here.  No return value.  The variables
        # self.cost_table and self.routes should reflect the current
        # shortest paths.
        #
        # Use self.LSA to get the topology information for this
        # network (see the lab write-up for details).  Remember that
        # self.routes maps node addresses to links.  If you need
        # access the link out of this Router to another node, use
        # self.getlink().

        #initializing cost_table
        init_costs = [(node, self.INFINITY) if node != str(self.address) else (node, 0) for node in nodes ]
        self.cost_table = dict(init_costs)
        trace_path = dict() #for each (non-self) node, records the parent(the expanded node to get to it)

        while len(init_costs) != 0:
            #pop the min_cost node from the pq
            init_costs.sort(key = lambda node: self.cost_table[node[0]])
            cur_node = init_costs.pop(0)[0]
           
            #expand current node and update path cost. 0th entry of LSA is seq num
            for nbr, lnk_cost in self.LSA[cur_node][1:]:
                cur_cost = self.cost_table[nbr]
                new_cost = lnk_cost + self.cost_table[cur_node]
                if((new_cost < cur_cost or nbr not in self.cost_table) and new_cost < self.INFINITY):
                    trace_path[nbr] = cur_node
                    self.cost_table[nbr] = new_cost

        #for each node, start from that node and trace back to the first node out of 'self' in its path
        for node in trace_path:
            cur_node = node
            while trace_path[cur_node] != str(self.address): 
                cur_node = trace_path[cur_node]
            self.routes[node] = self.getlink(cur_node)
                    
            
                
                
                
                
                
                

        
        
