import os

def detect_mpi_version():

    #Need to import nsim/config/nsimconf to find out about mpi version
    #(this is not perfect of course), which is relative to
    #nsim/interface/nmag or
    #nsim/interface/nsim or

    import nsim.snippets
    nsimpath = nsim.snippets.get_absolute_librarypath(nsim)[0]

    import sys
    newsearchpath = os.path.join(nsimpath,"../../config")

    print "Looking for file %s" % newsearchpath

    sys.path.append(newsearchpath)
    import nsimconf as conf
    sys.path.pop()
    
    print conf.mpich_ldflags
    
    if "mpich2" in conf.mpich_ldflags:
        print "Found MPICH2"
        return 'mpich2'
    elif "mpich" in conf.mpich_ldflags:
        print "Found MPICH1"
        return 'mpich1'
    else:
        print "Found NO mpi (or unknown: %s)" % conf.mpich_ldflags
        return "unknown"



if __name__=="__main__":

    version = detect_mpi_version()
    print "MPICH version detected is %s." % version


