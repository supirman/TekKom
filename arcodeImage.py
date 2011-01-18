import arcode
import Image, numpy

import array

class ArithmeticCodeImage (arcode.ArithmeticCode):
    
    def _init_(self):
        super(ArithmeticCodeImage,self)
    
    def encode(self, input_file_name, output_file_name):
        f_tmp = open("tmp.in","wb")
        im = Image.open( input_file_name)
        im = im.convert("L") #to grayscale
        a = numpy.asarray(im)
        a.tofile(f_tmp)
        f_tmp.close()
        super(ArithmeticCodeImage,self).encode(self, "tmp.in", output_file_name)
        
        
    
    def decode_file(self, input_file_name, output_file_name):
        
        super(ArithmeticCodeImage,self).encode(self, output_file_name,"tmp.out")
        f_tmp = open("tmp.out","wb")
        
        
        out = array.fromfile(f_tmp)
        im = Image.fromarray(out)
        im.save(output_file_name)
        
        
        