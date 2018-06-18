import numpy, sys

from channel import ChannelEncoder, ChannelDecoder


#find mod2 of the input array
def mod2(A):
    for i in range(2):
        A[A%2==i] = i
    return A

#check if two arrays are equal
def equal(x, y):
    return (x == y).all()


'''
A linear block encoder is just one type of channel encoder; we'll look
at another in PS3.
'''
class BlockEncoder(ChannelEncoder):

    def __init__(self):
        super(BlockEncoder, self).__init__()

    '''
    Here, you should implement the linear encoder. The input, bits,
    will be a numpy array of integers (each integer is 0 or 1).
    '''
    def encode(self, A, bits):
        codewords = []
        k, p = A.shape
        G = numpy.concatenate((numpy.eye(k),A), axis = 1)
        msgs = numpy.split(bits, int(bits.size/k))
        for msg in msgs:
            codeword = mod2(numpy.dot(numpy.reshape(msg, (1,k)),G))
            codewords.append(codeword)

        output = numpy.concatenate(codewords)
        return output.flatten().astype(int)
    
class SyndromeDecoder(ChannelDecoder):

    def __init__(self):
        super(ChannelDecoder, self).__init__()

    '''
    Here you should implement the syndrome decoder.
    
    Please set up the syndrome table before you perform the decoding
    (feel free to set up a different function to do this).  This will
    result in a more organized design, and also a more efficient
    decoding procedure (because you won't be recalculating the
    syndrome table for each codeword).
    '''
    def decode_single(self,codeword, n, k, A, G):
        
        #getting the databits and parity bits from codeword
        received_dbits = codeword[:k-n]
        received_pbits = codeword[k-n:]

        #getting the syndromes. i.e. the first K columns of the partiy check matrix H
        A_t = numpy.transpose(A)
        syndromes = numpy.split(A_t, k , axis = 1)

        #calculating the syndrome bits from codeword [k|p]
        computed_pbits = numpy.split(mod2(numpy.dot(numpy.reshape(received_dbits,(1,k)),G)), [k], axis = 1)[1]
        syndrome_bits = numpy.transpose(mod2(received_pbits + computed_pbits)).astype(int)
        
        #checking if there's a match in syndromes and correcting error    
        for i in range(len(syndromes)):
            if equal(syndromes[i], syndrome_bits):
                received_dbits[i]^=1

        return received_dbits
    
    def decode(self, A, bits):

        k, p = A.shape
        n = k+p
        G = numpy.concatenate((numpy.eye(k),A), axis = 1)
        received = numpy.split(bits, int(bits.size/n))
        messages = []
        
        for codeword in received:
            messages.append(self.decode_single(codeword, n, k, A, G))

        output = numpy.concatenate(messages)
        return output.flatten()
    

        
