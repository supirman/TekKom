import sys
import getopt
import os

import arcode
#import arcodeImage

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

if __name__ == "__main__":

    encode = None
    use_static_model = True
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
    
    ar = arcode.ArithmeticCode(use_static_model) if not image else arcodeImage.ArithmeticCodeImage()

    if encode:
        ar.encode_file(input_file, output_file)
    else:
        ar.decode_file(input_file, output_file)
