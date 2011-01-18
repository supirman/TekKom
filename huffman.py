"""
Tugas Teknik Kompresi - Huffman
5107100026	Dimas Radityo
5107100062	Firman Rosdiansyah
**Butuh koneksi internet/intranetITS untuk mengambil data**
"""


from itertools import groupby
import heapq
import struct


import sys
import getopt
import os
#import Image # Python PIL butuh install libary, jika belum ada

def makeHuffTree(symbolTupleList):
   
   trees = list(symbolTupleList)

   heapq.heapify(trees)
   while len(trees) > 1:
      childR, childL = heapq.heappop(trees), heapq.heappop(trees)
      parent = (childL[0] + childR[0], childL, childR)
      heapq.heappush(trees, parent)
      
   return trees[0]

def printHuffTree(huffTree, prefix = ''):
   if len(huffTree) == 2:
      print repr(huffTree[1]),'\t:', prefix

   else:
      printHuffTree(huffTree[1], prefix + '0')
      printHuffTree(huffTree[2], prefix + '1')

codes = {}
def codeHuff(huffTree, prefix = ''):
   if len(huffTree) == 2:
      codes[huffTree[1]]=(prefix,huffTree[0]) #menyimpan hasil encode dan frekuensi

   else:
      codeHuff(huffTree[1], prefix + '0')
      codeHuff(huffTree[2], prefix + '1')

def countProb(input):
   filesize=len(input)
   dataProb = [(len(list(b)),a) for a,b in groupby(sorted(input))]
   return dataProb

def read_header(f_in):
    """Reads a huffman header."""
    header = f_in.read(1024) # 256 symbols, 4 bytes each
    unpacked_header = struct.unpack('256I', header)
    
    return [(weight,chr(ch_indx) ) for ch_indx, \
                            weight in enumerate(unpacked_header) if weight]
   

def urlTestCase(url):
   import urllib
   return url,urllib.urlopen(url).read(),{},""

def bandingkanUkuran(source, hasil):
   print len(source),",",len(hasil)/8,"=>",len(hasil)*100/len(source)/8,"%"
   
def str2byte(source, f_out):
   byte_len , sisa = divmod (len(source),8)
   bins = [source[i << 3:(i + 1) << 3] for i in xrange(byte_len)]
   obstrs = [int(obstr, 2) for obstr in bins]
   
   if sisa:

      obstrs.append(int(source[-sisa:].ljust(8, '0'), 2))

   obstrs.append((8 - sisa) % 8)
   
   #f_out.write(struct.pack('%dB' % len(obstrs), *obstrs))
   #f_out.close()
   return obstrs

def write_header(f_out_obj, frequency_table1):
      """Write to file output a huffman header."""
      frequency_table = {}
      
      for i in xrange(256) :
         
         
         try :
            frequency_table[chr(i)] = 0
            frequency_table[chr(i)] = frequency_table1[chr(i)][1]
         except :
            frequency_table[chr(i)] = 0
         
      header = (struct.pack('I', frequency_table[chr(i)]) \
                for i in xrange(256))
      
      f_out_obj.write(''.join(header))

def dec2bin(dec_list):
    """
    Converts a sequence of decimal numbers to binary representation
    and return a big string of 0's and 1's.
    """
    # calculate and store binary codes for the 256 symbols
    bincodes = dict((k, ''.join(['1' if ((1 << i) & k) else '0' \
                           for i in xrange(7, -1, -1)])) for k in xrange(256))

    return ''.join([bincodes[dec] for dec in dec_list])



def read_encoded(file_obj):
    """Reads a file compressed by huffman algorithm."""
    
    content = [ch for line in file_obj for ch in line]
    print "c"

    bstr = dec2bin(struct.unpack('%dB' % len(content), ''.join(content)))
    bstr = bstr[:-8 -int(bstr[-8:], 2)] # remove end code and extra bits
    
    # return a big string of 0's and 1's
    return bstr

def decode_huffman(f_out_obj, root, binstr):
   
   start = root
   
   for b in binstr:
      root = root[1] if b == '0' else root[2]
      
      if len(root) == 2:
      
          f_out_obj.write("".join(root[1]))
          root = start

def show_usage():
    # Extract the name of this file from the command line
    this_file = sys.argv[0:][0]                     # full path
    this_file = (os.path.split(this_file))[1]       # name only

    print 'Usage: ',  this_file,  ' <options>\n'
    print 'options:\n'
    print '  -c : Encode input file to output file.'
    print '  -d : Decode input file to output file.'
    print '  -i <filename> : Name of input file.'
    print '  -o <filename> : Name of output file.'
    print '  -h | ?  : Print out command line options.\n'

def encode_file(input_file_name, output_file_name):
   f_in = open(input_file_name,"r")
   input = f_in.read()
   huffTree = makeHuffTree(countProb(input))
   codeHuff(huffTree)
   hasilEncode="".join([codes[a][0] for a in input])
   
   f_out= open(output_file_name,"w")
   write_header(f_out,codes)
   
   bin_ar= str2byte(hasilEncode,f_out)
   f_out.write(struct.pack('%dB' % len(bin_ar), *bin_ar))
   f_out.close()
   

def decode_file(input_file_name, output_file_name):
   f_in = open(input_file_name,"r")
   
   tree=makeHuffTree(read_header(f_in))
   binstr = read_encoded(f_in)
   
   f_out = open(output_file_name,"w")
   decode_huffman(f_out,tree,binstr)
   
   f_out.close()
   f_in.close()
   
   pass

if __name__ == '__main__':


   encode = None

   image = False
   input_file = ''
   output_file = ''

   # Parse command line options
   opts, args = getopt.getopt(sys.argv[1:], 'acdh?i:o:',
       ['help','gambar', 'encode', 'decode', 'input=', 'output='])

   for o, a in opts:
       if o in ('-g', '--gambar'):
           print "test"
           try:
               import Image, numpy
           except ImportError, e:
               print "Gagal import modul Image"
               pass # module doesn't exist, deal with it.
           image = True
       if o in ('-c', '--encode'):
           encode = True
       if o in ('-d', '--decode'):
           encode = False
       if o in ('-i', '--input'):
           input_file = a
       if o in ('-o', '--output'):
           output_file = a
       if o in ('-h', '-?', '--help',):
           show_usage()
           exit()

   # Validate command line options
   if len(input_file) == 0:
       print 'Error: Input file name is required.\n'
       show_usage()
       exit()

   if len(output_file) == 0:
       print 'Error: Output file name is required.\n'
       show_usage()
       exit()

   if encode == None:
        print 'Error: Encoding or Decoding must be specified.\n'
        show_usage()
        exit()

    # Encode/Decode specified file
   #print "image",image
   #ar = arcode.ArithmeticCode(use_static_model) if not image else arcodeImage.ArithmeticCodeImage()

   if encode:
        encode_file(input_file, output_file)
   else:
        decode_file(input_file, output_file)

   
   
   
   """
   testcase = {}
   #Testcase 1
   
   testcase[0] = urlTestCase("http://mirror.its.ac.id/pub/ubuntu/dists/karmic/Release")
   #print testcase[0][1]
   huffTree = makeHuffTree(countProb(testcase[0][1]))
   codeHuff(huffTree)
   #print codes
   print "Tingkat Kompresi ",testcase[0][0]
   #print len(testcase[0][1])*8,len("".join([codes[a] for a in testcase[0][1]]))

   hasilEncode="".join([codes[a][0] for a in testcase[0][1]])
   
   f_out= open("out1.huff","w")
   
   write_header(f_out,codes)
   
   bin_ar= str2byte(hasilEncode,f_out)
   f_out.write(struct.pack('%dB' % len(bin_ar), *bin_ar))
   f_out.close()
   
   bandingkanUkuran(testcase[0][1],hasilEncode)
   
   #Testcase 2

   codes = {}
   testcase[1] = urlTestCase("http://www.its.ac.id/pengumuman/Logodies50bundar.jpg")
   
   huffTree = makeHuffTree(countProb(testcase[1][1]))
   codeHuff(huffTree)
   #printHuffTree(huffTree)
   hasilEncodeImage="".join([codes[a][0] for a in testcase[1][1]])
   print "Tingkat Kompresi ",testcase[1][0]
   bandingkanUkuran(testcase[1][1],hasilEncodeImage)
   """
   
   #f = open("image.jpg","w")
   #f.write(testcase[1][1])
   
   #print type(testcase[1][1])
   
   
   #im = Image.open("image.jpg")
   #print im.histogram()
   #im.save("image.bmp","BMP")
   #if im.mode != "L":
   # im = im.convert("L")
                    
   #im.show()
   #im.save("imageG.bmp","BMP")

   #print im.histogram()
   """
   f = open("out1.huff","r")
   prob = read_header(f)
   binstr=read_encoded(f)
   print prob
   tree=makeHuffTree(prob)
   f_out_dec = open("out.dec.txt","w")
   decode(f_out_dec,binstr,tree)
   f_out_dec.close()
   f.close()
   """
   