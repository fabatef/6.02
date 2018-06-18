import numpy
import operator

from collections import defaultdict

from channel import ChannelEncoder, ChannelDecoder

class ConvolutionalEncoder(ChannelEncoder):

    def __init__(self, G):
        super(ChannelEncoder, self).__init__()
        self.G = G
        self.r, self.K = G.shape

    def encode(self, received_voltages):
        #no padding with zeros...so only keep the first len(received_messages) convolution results
        p_i = [numpy.convolve(g_i, received_voltages)[:len(received_voltages)] for g_i in self.G]
        result = numpy.array([p_bit for packed in zip(*p_i) for p_bit in packed])
        return numpy.mod(result,2)

class ViterbiDecoder(ChannelDecoder):

    def __init__(self, G):
        super(ChannelDecoder, self).__init__()
        self.G = G
        self.r, self.K = G.shape
        self.n_states = 2**(self.K-1)      # number of states
        self.states = range(self.n_states) # the states themselves

        # States are kept as integers, not binary strings or arrays.
        # For instance, the state "10" would be kept as "2", "11" as
        # 3, etc.

        # self.predecessor_states[s] = (s1, s2), where s1 and s2 are
        # the two predecessor states for state s (i.e., the two states
        # that have edges into s in the trellis).
        self.predecessor_states = [((2*s+0) % self.n_states, (2*s+1) % self.n_states) for s in self.states]

        # self.expected_parity[s1][s2] = the parity when transitioning
        # from s1 to s2 ('None' if there is no transition from s1 to
        # s2).  This is set up as a dictionary in init, for
        # efficiency.  For inefficiency, you could call
        # calculate_expected_parity() each time.
        self.expected_parity = defaultdict(lambda:defaultdict(float))
        for (s1, s2) in [(s1, s2) for s1 in self.states for s2 in self.states]:
            self.expected_parity[s1][s2] = self.calculate_expected_parity(s1, s2) if s1 in self.predecessor_states[s2] else None

        # Your code will update these variables
        self.PM = None
        self.Predecessor = None

    def calculate_expected_parity(self, from_state, to_state):

        # x[n] comes from to_state
        # x[n-1] ... x[n-k-1] comes from from_state
        x = ((to_state >> (self.K-2)) << (self.K-1)) + from_state

        # Turn the state integer into an array of bits, so that we can
        # xor (essentially) with G

        z = ViterbiDecoder.int_to_bit_array(x, self.K)
        return self.G.dot(z) % 2

    # Converts integers to bit arrays.  Useful if you find it
    # difficult to operate with states that are named as integers
    # rather than bit sequences.  You will likely not need to call
    # this function at all.
    @staticmethod
    def int_to_bit_array(i, length):
        return numpy.array([int(q) for q in (length-len(bin(i)[2:]))*'0'+bin(i)[2:]])

    # Finds the most significant bit in a (self.K -1) bit sequence.
    # Used it for traceback
    def msb(self, num):
        return num >> (self.K -2)
    def viterbi_step(self, n, received_voltages):
        # a list of the path metrics for each state at a given time n (index corresponds to state)
        PMs = []
        
        #the optimal predecessors for each state at a given time n (index corresponds to state)
        preds = []
        for state in range(self.n_states):
            
            #predecessors of state s
            pred_1, pred_2 = self.predecessor_states[state]
            
            #expected parity bits from the two possible paths into state s
            expected_1= self.calculate_expected_parity(pred_1, state)
            expected_2 = self.calculate_expected_parity(pred_2, state)

            # calculate the path metric(PM) for state s at time n with the viterbi algorithm using DP:
            # PM[s,n] = min (PM[pred_1, n-1] + BM[pred_1 -> s], PM[pred_2, n-1] + BM[pred_2 -> s])
            choice = [self.branch_metric(expected_1, received_voltages) + self.PM[pred_1,n-1], \
                      self.branch_metric(expected_2, received_voltages) + self.PM[pred_2, n-1]]

            PM_current_state= min(choice)
            PMs.append(PM_current_state)
            
            optimal_pred = pred_1 if choice.index(PM_current_state)==0 else pred_2 
            preds.append(optimal_pred)

        
        #updating the columns of PM and Predcessor    
        self.PM[:,n], self.Predecessor[:,n] = PMs, preds

    def branch_metric(self, expected, received, soft_decoding=False):
        #finding the euclidean distance between expected and received voltages
        BM_soft = lambda expected,received: sum([(exp - rec)**2 for exp, rec in zip(expected,received)])
        
        if soft_decoding:
            return BM_soft(expected,received)
        else:
            digitized_received = [1 if sample > 0.5 else 0 for sample in received]
            return sum(map(operator.xor, digitized_received, expected))


    def most_likely_state(self, n):
        PM_vals= self.PM[:,n]
        return PM_vals.argmin() #returns the index of the minimum element

    def traceback(self,s,n):
        msg = []
        current_state = s
        while n!=0:
            # the most significan bit of the current state is the message bit that transitioned optimal_pred to state s. 
            edge= self.msb(current_state) 
            msg.append(edge)
            current_state = self.Predecessor[current_state,n] #trace back to the prev state
            n-=1
            
        msg.reverse()

        return msg 
        
    def decode(self, received_voltages):

        max_n = (len(received_voltages) // self.r) + 1

        # self.PM is the trellis itself; rows are states, columns are
        # time.  self.PM[s,n] is the metric for the most-likely path
        # through the trellis arriving at state s at time n.
        self.PM = numpy.zeros((self.n_states, max_n))

        # at time 0, the starting state is the most likely, the other
        # states are "infinitely" worse.
        self.PM[1:self.n_states,0] = 1000000

        # self.Predecessor[s,n] = predecessor state for s at time n.
        self.Predecessor = numpy.zeros((self.n_states,max_n), dtype=numpy.int)

        # Viterbi Algorithm:
        n = 0
        for i in range(0, len(received_voltages), self.r):
            n += 1
            # Fill in the next columns of PM, Predecessor based
            # on info in the next r incoming parity bits
            self.viterbi_step(n, received_voltages[i:i+self.r])

        # Find the most-likely ending state, and traceback to
        # reconstruct the message.
        s = self.most_likely_state(n)
        result = self.traceback(s,n)
        return result

