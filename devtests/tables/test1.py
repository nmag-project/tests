#!/sw/bin/python2.4

"""write arrays, create group with arrays. Good for saving mesh, say."""


import tables
import numarray

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

a = numarray.arange(nfloats, type=numarray.Float64, shape=(nvectors,3))
# Save it on the HDF5 file
hdfarray = fileh.createArray(root, 'array_f', a, "%d-3 matrix"%nvectors)
hdfarray = fileh.createArray(root, 'array_g', a, "3-2 tensor array")


group = fileh.createGroup("/", 'mesh', 'mesh data')
print "Group '/mesh' created"

#create group and create array in that group
hdfarray = fileh.createArray(group, 'nodepos', a, "node positions")


fileh.close()

#f=tables.openFile('test1.h5','r')
#for x in f:
#    print x
