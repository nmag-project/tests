"""For debugging purposes we have written a binary file bem.log containing the
boundary element matrix which has been computed by HLib. This file converts
the binary format into an ASCII format."""
import struct
import numpy

fname = '/tmp/bem.log'
outputfile = 'bem.dat'

data = open( fname ).read()

nrow,ncol = map(int,struct.unpack('d'*2,data[0:16]))

bem = numpy.zeros((nrow,ncol))

outputfile = open("bem.dat",'w');

outputfile.write("%6d     %6d\n" % (nrow,ncol))
for i in range(nrow):
    for j in range(ncol):
        start = 16+8*( i*ncol+j )
        end = start+8
        bem[i,j] = struct.unpack('d',data[start:end])[0]
        outputfile.write("%12.10f\n" % bem[i,j])

outputfile.close
