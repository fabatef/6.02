import argparse
import array
import math

from bitstring import BitString

def initialize(encode):
    Table = {}
    if encode:
        for i in range(256):
            Table[chr(i)]= i
    else:
        for i in range(256):
            Table[i] = chr(i)
    return Table
    

class LZW():

    def __init__(self, word_size=9):
        self.word_size = word_size

    #message: list of strings
    def encode(self, message):
            
        #initializing Table[0 to 255] to corresponding ASCII charaters
        Table = initialize(encode = True)
        #print (message, len(message))
        
        #initializing table index and P
        index = 256
        counter = 0
        output = []
        P = ''
        #LZW compression algorithm
        while counter != len(message)+1:
            try:
                C = message[counter]
            except IndexError: # for the last iteration, C is empty so just return P and exit
                output.append(Table[P])
                break    
            if P + C in Table:
                P = P + C                    
            else: 
                output.append(Table[P])
                Table[P + C] = index
                index+=1
                P = C
            counter+=1

            #if index > 2**self.word_size-1: #if the dictionary outgrew the word_size, re_initialize
            if index > 2**self.word_size:
                Table = initialize(encode = True)
                index = 256
        #print (index, max(output))
        #print (output, len (output))
        packed_output = BitString()

##        if index > 2**self.word_size-1: #if the dictionary outgrew the word_size, re_initialize
##            packed_output.pack_numbers(output, math.ceil(math.log2(max(output))))#math.ceil(math.log2(index)
##        else:
        packed_output.pack_numbers(output, self.word_size)
        print (packed_output.data, len(packed_output))
        return packed_output 
    

    def decode(self, bits):

        
        #initializing Table[chr(0) to chr(255)] to corresponding indices
        Table = initialize(encode = False)
            
        #getting indices of the codewords from the BitString
        #trial = BitString()
        #trial.pack_number(97, self.word_size)
        #print ('BITS: ', bits.unpack_number(self.word_size), trial, trial.unpack_number(self.word_size))
##        print ('BITS DATA: ' , bits.data)
##        codewords = []
##        while len(bits) != 0:
##            #print ('LEN BITS:', len(bits))
##            index = bits.unpack_number(self.word_size)
##            codewords.append(index)
##            #print ('RESULT:', index)
##        codewords.reverse()
##        print (len(codewords))
        codewords = bits.unpack_all_numbers(self.word_size)
        #codewords.reverse()
        print (codewords)
        
        #LZW decompression algorithm
        index = 256
        #initalizing the output with the first codeword
        P = Table[codewords[0]]
        output = [P]
        #print (codewords[1:])
        for cw in codewords[1:]:
            try:
                C = Table[cw]
                entry = P + C[0]
                #print (C, cw, entry)
                output.append(C)
            except KeyError:
                entry = P + P[0]
                C = entry
                #print ('special', P, entry)
                output.append(entry)
                
            Table[index] = entry
            P = C
            index+=1
        #print (output, len(''.join(output)))
            if index > 2**self.word_size:
                Table = initialize(encode = False)
                index = 256

        return ''.join(output)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename', type=str, help='filename to compress or decompress', default='test')
    parser.add_argument('-d', '--decompress', help='decompress file', action='store_true')
    args = parser.parse_args()

    lzw = LZW()

    if  not args.decompress:
        # read in the file
        f = open(args.filename, 'rb')
        compressed = [chr(k) for k in array.array("B", f.read())]
        f.close()
        # encode and output
        x = lzw.encode(compressed)
        new_filename = args.filename + '.encoded'
        x.write_to_file(new_filename)
        print("Saved encoded file as %s" % new_filename)

    else:
        b = BitString()
        b.read_in_file(args.filename)
        x = lzw.decode(b)
        new_filename = args.filename + '.decoded'
        with open(new_filename, "w") as f:
            f.write(x)
        print("Saved decoded file as %s" % new_filename)
