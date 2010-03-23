import nmag
import os

def find_mpi_version():

    import nsim.snippets
    nsimpath = nsim.snippets.get_absolute_librarypath(nsim)[0]

    import sys
    newsearchpath = os.path.join(nsimpath,"../../tests/regression/nsim/mpi")

    print "Looking for file in %s" % newsearchpath

    sys.path.append(newsearchpath)
    import detect_mpi_version
    sys.path.pop()
    
    return detect_mpi_version.detect_mpi_version()
    
def test_run_mpi_bigbar():

    import sys,os

    proper_sysargv = sys.argv
    sys.argv = sys.argv[0:1]

    #work out in which directory the data files are
    org_dir = os.getcwd()
    os.chdir(os.path.split(__file__)[0])

    mpiversion = find_mpi_version()


    if mpiversion == 'mpich1':
        print "Doing MPICH1 test"
        os.system("make clean run-mpich1 results-mpich1 > make.out")
    else:
        print "Doing MPICH2 test"
        os.system("make clean run-mpich2 results-mpich2 > make.out")

    os.chdir(org_dir)


def datafile2numpy(filename):

    import numpy
    times = []
    Ms = []

    lines = open(filename,'r').readlines()
    for line in lines:
        bits = line.split()
        assert len(bits)==4,"Error in '%s' -- expect 4 columns" % filename
        times.append(float(bits[0]))
        Ms.append(map(float,bits[1:4]))

    times_numpy = numpy.array(times)
    Ms_numpy = numpy.array(Ms)

    return times_numpy,Ms_numpy






def do_differencecheck():
    import numpy

    #Test against nmag data from 25 July 2008 (rev 5664).
    t,M = datafile2numpy('../results/nmag4_M_r5664.dat')
    t2,M2 = datafile2numpy('../results/nmag4mpi_M.dat')

    #we expect the difference between newer nmag runs and this 'old' run to be very, very small.
    #
    #to get a feel for the expected deviation, here is the data when comparing with an older
    #(nmag3) data set:

    #  t2,M2 = datafile2numpy('../results/nmag3_M_20070328.dat')
    #
    # output:
    #       largest value in data set is 854456.261653
    #       reltol we tolerate is 0.000200
    #       abstol we tolerate is 170.891252
    #       max dev is 133.943901, relative error is 0.000157

    #So we use a relative allowed tolerance of 0.02% for the future.
    #

    #Note that when plotting the nmag3 and nmag4 data, then the curves pretty much coincide
    #with OOMMF and magpar data; so it seems we can trust them.
    #The reason for comparing with nmag data is thatwe have that available at exactly the
    #right moments in time (so we don't need to interpolate Mx, My, Mz for different t).
    #
    #(fangohr 29/07/2008)



    print "t.shape=",t.shape
    print "t2.shape=",t2.shape
    
    #make sure t and t2 are the same
    assert numpy.max(t-t2)==0.,"times of saved data disagree in the two files"

    maxval1 = numpy.max(M)
    maxval2 = numpy.max(M2)

    maxval = min(maxval1,maxval2)

    #tolerance we accept: 1 percent 
    reltol = 0.0002

    abstol = maxval*reltol
    print "largest value in data set is %f" % maxval
    print "reltol we tolerate is %f" % reltol
    print "abstol we tolerate is %f" % abstol


    maxdev = numpy.max(M-M2)
    print "max dev is %f, relative error is %f" % (maxdev,maxdev/maxval)
    assert abs(maxdev) < abstol,"Error=%f is larger than tolerance=%f" % (maxdev,abstol)
    print "Test passed"

    return t,t2,M,M2




def test_data_for_correctness():
    
    import sys, os

    proper_sysargv = sys.argv
    sys.argv = sys.argv[0:1]

    #work out in which directory the data files are
    org_dir = os.getcwd()
    os.chdir(os.path.split(__file__)[0])

    #we have data from end of July 2008 which matches OOMMF and magpar
    #data (roughly), so we take this as a base line


    do_differencecheck()

    os.chdir(org_dir)

    


if __name__=="__main__":

    print find_mpi_version()
    #test_run_mpi_bigbar()
    #t,M,t2,M2=do_differencecheck()

    #import nmag
    #nmag.ipython()


