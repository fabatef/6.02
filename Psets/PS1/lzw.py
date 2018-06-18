import argparse
import array
import math

from bitstring import BitString
#helper function to initalize dictionaries for encode/decode
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

    def __init__(self, word_size=16):
        self.word_size = word_size

    #message: list of strings
    def encode(self, message):
            
        #initializing Table[0 to 255] to corresponding ASCII charaters
        Table = initialize(encode = True)
        
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

            #if the dictionary outgrew the word_size, re_initialize the dictionary
            if index > 2**self.word_size:
                Table = initialize(encode = True)
                index = 256
                
        packed_output = BitString()
        packed_output.pack_numbers(output, self.word_size)
        return packed_output 
    

    def decode(self, bits):

        
        #initializing Table[chr(0) to chr(255)] to corresponding indices
        Table = initialize(encode = False)
            
        #getting indices of the codewords from the BitString
        codewords = bits.unpack_all_numbers(self.word_size)
        


        index = 256
        #initalizing the output and P with the first codeword
        P = Table[codewords[0]]
        output = [P]
        #LZW decompression algorithm
        for cw in codewords[1:]:
            try:
                C = Table[cw]
                entry = P + C[0]
                output.append(C)
            except KeyError:
                entry = P + P[0]
                C = entry
                output.append(entry)
                
            Table[index] = entry
            P = C
            index+=1

            #Just like the incoder, when the dictionary hits max_size, re_initialize the dictionary
            if index > 2**self.word_size:
                Table = initialize(encode = False)
                index = 256

        return ''.join(output)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename', type=str, help='filename to compress or decompress', default='PS1_change.dat')
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
