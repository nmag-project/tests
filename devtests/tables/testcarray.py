

#!/sw/bin/python2.4

"""write arrays, create group with arrays. Good for saving mesh, say."""


import tables
import numpy
import tables

# Open a new empty HDF5 file
fileh = tables.openFile("test1.h5", mode = "w")
# Get the root group
root = fileh.root

# Create a 3-d array of floats
#a = arange(64, type=Float64, shape=(2,4,8))
MB = 1024*1024
size = 10*MB
nfloats = size / 8
nvectors = nfloats / 3
nfloats = nvectors*3

print "nfloats are",nfloats
shape = (nvectors,3)
#a = numarray.arange(nfloats, type=numarray.Float64, shape=shape)
a = numpy.random.uniform(size=shape)*0
print a[0:10]
# Save it on the HDF5 file
print "size of data is ",nfloats*8.0/MB

#filters = tables.Filters(complevel=5, complib="bzip2")
filter = tables.Filters(complevel=5, complib="zlib")

#observation: compressing random data gives a space gain of 10% and is
#slower by a factor 20 (approximately). THis is independent of the
#library (zlib, bzip2) and the complevel (tried 0, 5, 10).
#
#Seems not worth it. Should check again with real data (which is more correlated).
# Hans



import time
time1 = time.time()

chunk = tables.Float64Atom(shape = shape)

ca = fileh.createCArray(root, 'carray', shape, chunk, filters=filter) 
ca[:] = a

#hdfarray = fileh.createArray(root, 'array_f', a, "3-2 tensor array")
#hdfarray = fileh.createArray(root, 'array_g', a, "3-2 tensor array")

#group = fileh.createGroup("/", 'detector', 'Detector information')
#print "Group '/detector' created"

#create group and create array in that group
#hdfarray = fileh.createArray(group, 'array_g', a, "3-2 tensor array")


fileh.close()
time_taken = time.time()-time1
print "time taken is ",time_taken

f=tables.openFile('test1.h5','r')
for x in f:
    print x
