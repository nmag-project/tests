import nmag
import os


NCPU = 4

#work out in which directory the data files are
org_dir = os.getcwd()

if __file__[0]=='/': #absolute path, displayed when file is imported
    thispath = __file__
else:
    thispath = os.path.join(os.getcwd(), __file__)
    

os.chdir(os.path.split(thispath)[0])

def test_nr_cpus():
    os.chdir(os.path.split(thispath)[0])
    command = "make mpi-hello > make.out"
    print "Running '%s'" % command
    os.system(command)

    assert os.path.exists('output.txt')

    import time
    time.sleep(1)
    os.chdir(org_dir)

def test_things():
    """The output we expect is

    MPI-status: There are 4 nodes (this is the master, rank=0)
    [Node   0/4] Hello from eta
    [Node   2/4] Hello from eta
    [Node   3/4] Hello from eta
    [Node   1/4] Hello from eta

    """

    os.chdir(os.path.split(thispath)[0])
    
    f=open('output.txt','r')
    lines = f.readlines()

    seen_cpu = NCPU*[False]
    
    for line in lines:
        if line.count('Node'):
            bits = line.split()
            cpu = bits[1].split('/')[0]
            print "Found CPU %s" % cpu
            cpu_id = int(cpu)
            seen_cpu[cpu_id] = True
        elif line.count('MPI-status'):
            bit0 = line.split('nodes')[0]
            size = bit0.split()[-1]
            print "Size is %s" % size
            assert NCPU == int(size),"Expected %d CPUs, not %d" % (NCPU,int(size))


    nr_cpu_seen = seen_cpu.count(True)

    print "Have seen %d/%s cpus" % (nr_cpu_seen,NCPU)


    homedir = os.path.expanduser('~')
    if os.path.exists(os.path.join(homedir,'.mpd.conf')):
        msg=""
    else:
        msg="""\n\n    If you intend to use MPICH2 to run Nmag(nsim) in
    parallel, you need to have a file ~/.mpd.conf in your home
    directory.


    One way to do this is:
    
      cd $HOME
      touch .mpd.conf
      chmod 600 .mpd.conf
      
    and then use an editor to insert a line like
    
      MPD_SECRETWORD=mr45-j9z

      """
            
    assert nr_cpu_seen == NCPU, \
      "Not all cpus found (seen %d/%d) %s" % (nr_cpu_seen,NCPU,msg)

    os.chdir(org_dir)

if __name__ == "__main__":
    test_nr_cpus()
    test_things()
