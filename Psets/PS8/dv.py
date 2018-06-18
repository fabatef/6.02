import random,sys,math

from PS8_netsim import *
import PS8_tests

class DVRouter(Router):
    INFINITY = 32

    def send_advertisement(self, time):
        # Do not change this function.  You do not need to modify it.
        adv = self.make_dv_advertisement()
        for link in self.links:
            p = self.network.make_packet(self.address, self.peer(link), 'ADVERT', time, color='red', ad=adv)
            link.send(self, p)        

    def process_advertisement(self, p, link, time):
        # Do not change this function.  You do not need to modify it.
        self.integrate(link, p.properties['ad'])

    def make_dv_advertisement(self):
        # TODO: Your code here
        # Should return a list of the form [(dest1, cost1), (dest2, cost2) ...]
        return [(dst, self.cost_table[dst]) for dst in self.routes]

    def link_failed(self, dead_link):
        # TODO: Your code here.  No return value.
        #
        # Take the appropriate action given that dead_link has failed.
        # The appropriate action will depend on how you design your
        # protocol.
        #
        # If you need to set a cost fo infinity, use self.INFINITY,
        # not INFINITY.

        # if the current node uses dead_link to get to any of the destination
        # nodes in the routing table, set the cost to INFINITY and the route to None
        for dst, route in self.routes.items():
            if route == dead_link:
                self.cost_table[dst] = self.INFINITY
                self.routes[dst] = None


    def integrate(self, link, advertisement):
        # TODO: Your code here.  No return value.  At the end of this
        # function, the variables self.cost_table and self.routes
        # should reflect the current shortest paths.
        # 
        # Recall that self.routes maps addresses to instances of the
        # Link class, and self.cost_table maps addresses to the
        # shortest path cost to that node.
        #
        # link is the link that delivered advertisement.  Use
        # link.cost to determine its cost.

        for dst, cost in advertisement:
            #if the dst is not in the routing table, update route and cost_table if the cost != inf
            if ((not dst in self.routes or self.routes[dst] == None) and link.cost + cost < self.INFINITY):
                self.cost_table[dst] = link.cost + cost
                self.routes[dst] = link
            else:
                new_cost = link.cost + cost
                #if the advert link is the cur route to dst, update the cost_table regardless
                if (self.routes[dst] == link):
                    self.cost_table[dst] = min(new_cost, self.INFINITY)
                    #if the new cost is inf, there's no longer a route
                    if (self.cost_table[dst] == self.INFINITY):
                        self.routes[dst] = None
                #if its a d/t link with a smaller cost, update the route and cost_table because you found a better route
                else: 
                    if(new_cost < self.cost_table[dst] and link.cost + cost < self.INFINITY):
                        self.cost_table[dst] = new_cost
                        self.routes[dst] = link
  
        
