"""This script plots the difference between the boundary element matrix
computed by nmag and HLib. Before running this script one should have
run the script read_bemlogfile.py."""
import pylab
from pylab import *
from scipy import mgrid
import numpy

def imsave(filename, X, **kwargs):
    """ Homebrewed imsave to have nice colors... """
    figsize=(array(X.shape)/100.0)[::-1]
    rcParams.update({'figure.figsize':figsize})
    fig = figure(figsize=figsize)
    axes([0,0,1,1]) # Make the plot occupy the whole canvas
    axis('on')
    fig.set_size_inches(figsize)
    imshow(X,origin='lower', **kwargs)
    savefig(filename, facecolor='black', edgecolor='black', dpi=100)


bemfile = open('./bem.dat','r')
hlibfile= open('../hlib_bem.dat','r')

data_bem = bemfile.readlines()
data_hlib = hlibfile.readlines()

bemfile.close()
hlibfile.close()

outputfile = open("output.dat","w")

bem_entries = data_bem[0].split()
bem_rows = int(bem_entries[0])
bem_cols = int(bem_entries[1])

hlib_entries = data_hlib[0].split()
hlib_rows = int(hlib_entries[0])
hlib_cols = int(hlib_entries[1])

assert (bem_rows == hlib_rows and bem_cols == hlib_cols),"The matrix data sets do not fit to each other."

diagonal = numpy.zeros(hlib_rows)
diagonal_counter = 0
difference = numpy.zeros((hlib_rows,hlib_cols))
ref_counter = 0
hlib_counter = 0
bem_counter = 0
for i in range(bem_rows):
    for j in range(bem_cols):
        bem_entries = data_bem[i*bem_cols+j+1].split()
        bem_value = float(bem_entries[0])
        hlib_entries = data_hlib[i*bem_cols+j+1].split()
        hlib_value = float(hlib_entries[0])
        difference[i,j] = hlib_value - bem_value
        outputfile.write(" %f   %f   %f\n" % (bem_value,hlib_value,difference[i,j]))
        ref_counter = ref_counter + 1
        if(i==j):
            assert (diagonal_counter < hlib_rows),"variable diagonal counter is getting too large"
            diagonal[diagonal_counter] = difference[i,j]
            diagonal_counter = diagonal_counter + 1
        
outputfile.close()

print "bem_counter: %d, hlib_counter: %d\n" % (bem_counter,hlib_counter)
print "The value of the reference counter is %d.\n" % ref_counter

title("Deviations of the diagonal elements")
xlabel("Diagonal elements")
ylabel("Deviation between bem and approximation")
plot(range(1,hlib_rows+1),diagonal)
show()
imsave('imsave.png', difference, cmap=cm.hot )
