import random,sys

from PS9_netsim import *
from PS9_util import *

class ReliableSenderNode(AbstractReliableSenderNode):

    def __init__(self,location,qsize,window,address=None,):
        self.network = None # This variable will be set by the following initialization methods
        AbstractReliableSenderNode.__init__(self,location,qsize,window,address=address)

    def reset(self):
        Router.reset(self)
        self.srtt = 0 #None
        self.rttdev = 0 #None
        self.timeout = 20    # arbitrary initial value
        # TODO: Your initialization code here, if you need any.  We've
        # already initialized self.srtt, self.rttdev, self.timeout
        # above.
        
        self.unacked_pkts = set()
        self.seqnum = 0 #seqnum counter
        
        self.alpha = 0.125 #TCP specs
        self.beta = 0.25 #TCP specs


    # Called every timeslot.  Decides whether to send a new packet, to
    # retransmit, or to do nothing.  If you need to send a packet in
    # this timeslot, use the send_packet() function.
    def reliable_send(self):
        cur_time = self.network.time

        if len(self.unacked_pkts) < self.window:
            pkt = self.send_packet(self.seqnum, cur_time)
            self.unacked_pkts.add(pkt)
            self.seqnum += 1
        
        # if no ACK received for unacked pkts and timeout passed, retransmit
        for pkt in self.unacked_pkts:
            if (cur_time - pkt.timestamp > self.timeout):
                self.send_packet(pkt.seqnum, cur_time)
                pkt.timestamp = cur_time
                
            

        
    # Invoked whenever an ACK arrives
    def process_ack(self, acknum, sender_timestamp):
        # TODO: Your code here
        unack_seqnums = dict((p.seqnum, p) for p in self.unacked_pkts)
        if acknum in unack_seqnums:
            self.calc_timeout(sender_timestamp) # Don't delete this!
            self.unacked_pkts.remove(unack_seqnums[acknum])

    # Called whenever an ACK arrives.  Should update the value of
    # self.timeout, as well as the values of self.srtt (smoothed
    # round-trip-time) and self.rttdev (mean linear RTT deviation).
    def calc_timeout(self, packet_timestamp):
        # TODO: Your code here
        cur_time = self.network.time
        r = cur_time - packet_timestamp
        #print ("R: ", r, "SRTT: ", self.srtt)
        self.srtt = self.alpha * r + (1 - self.alpha) * self.srtt
        dev = abs(r - self.srtt)
        self.rttdev = self.beta * dev + (1 - self.beta) * self.rttdev
        self.timeout = self.srtt + 4 * self.rttdev

    # Send a packet at the current time, with specified seqnum,
    # timestamp.  You do not need to edit this method.
    def send_packet(self, seqnum, pkt_timestamp):
        time = self.network.time
        xmit_packet = self.network.make_packet(
            self.address, self.stream_destination, 'DATA', time, 
            seqnum=seqnum, timestamp=pkt_timestamp)
        self.forward(xmit_packet)
        xmit_packet.start = time
        return xmit_packet

# ReliableReceiverNode extends Router to implement reliable
# receiver functionality with path vector routing.
class ReliableReceiverNode(AbstractReliableReceiverNode):
    def __init__(self,location,qsize,window,address=None):
        AbstractReliableReceiverNode.__init__(self, location, qsize, window,address=address)
        self.reset()

    def reset(self):
        AbstractReliableReceiverNode.reset(self)
        #TODO: Your code for initializing the receiver, if you need
        #any, should go here
        self.rcvbuf = set()

    # Invoked every time the receiver receivers a data packet from the
    # receiver.  Sends an ACK back, and does the rest of the necessary
    # processing.  Use self.send_ack() to send an ACK packet, and
    # self.app_receive() to send a data packet to the receiving
    # application. (self.app_receive() is defined in
    # AbstractReliableSenderNode, though you shouldn't need to know
    # anything about its internals.).  self.app_seqnum will tell you
    # the last sequence number that the receiving application received.
    def reliable_recv(self, sender, seqnum, packet_timestamp):
        self.send_ack(sender, seqnum, packet_timestamp)#always ACK reception!

        if (seqnum > self.app_seqnum): #don't enq packets you already sent to app
            self.rcvbuf.add(seqnum)

        rm = []
        for i in range(len(self.rcvbuf)):
            #print ("LOOKING FOR: " ,self.app_seqnum+1)
            if self.app_seqnum+1 in self.rcvbuf: 
                rm.append(self.app_seqnum + 1)
                self.app_receive(self.app_seqnum + 1)
            else:
                break
        #if self.window > 1:
            #print ("SENT: ", rm, "RCVBUF: ", self.rcvbuf)    
        for sent in rm:
            self.rcvbuf.remove(sent)
            

        
        

    # Send an ACK packet.  You do not need to modify this method.
    def send_ack(self, sender, seqnum, pkt_timestamp):
        time = self.network.time
        ack = self.network.make_packet(self.address, sender, 'ACK', time,
                                       seqnum=seqnum, timestamp=pkt_timestamp)
        self.forward(ack);
