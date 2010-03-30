"""This test program is called by py.test (from many directory levels above)."""

import nmag
import os

def test_gmsh_1_0_import():
    #py.test will pass on any command line arguments to the code it tests.
    #This will confuse nmag (as it doesn't know how to handle py.test's '-k'
    #and '--verbose' switches, etc.
    #
    #We thus manually delete all other entries that the name of the executable
    #from sys.argv.
    import sys

    proper_sysargv = sys.argv
    sys.argv = sys.argv[0:1]

    # work out in which directory the data files are
    org_dir = os.getcwd()
    os.chdir(os.path.split(__file__)[0])

    # Compute new data (this can take a while, will delete old data files
    # automatically)
    os.system("rm -fv sphere.nmesh &> test_stdoutstderr1.log")

    # Remove this line as it depends on having gmsh installed
    # os.system("make sphere.msh >> test_make_run1.out")
    #
    f = open("sphere.msh", "r")
    assert f.readline()[0:4] == "$NOD", \
      "gmsh file 'sphere.msh' has not been written correctly"
    f.close()

    os.system("make sphere.nmesh 2>&1 >test_stdoutstderr2.log")
    import nmesh

    mesh = nmesh.load("sphere.nmesh")

    n, expect = (len(mesh.points), 258)
    assert n == expect, ("Number of nodes has changed. "
                         "Expected %d, but got %d" % (expect,n))

    n, expect = (len(mesh.simplices), 677)
    assert n == expect, ("Number of simplices has changed. "
                         "Expected %d, but got %d" % (expect, n))

    n, expect = (len(mesh.simplicesregions), 677)
    assert n == expect, ("Number of simplicesregions has changed. "
                         "Expected %d, but got %d" % (expect, n))


    # For the number of links, we have seen 1687 and 1689. This seems 
    # to be non-deterministic behaviour from parmetis. We thus allow
    # a range of links.
    n, expect = (len(mesh.links), "1670-1700 (1687 and 1689 have been seen)")
    assert 1670 <= n <= 1700, ("Number of links has changed. "
                               "Expected %s, but got %d" % (expect, n))

    n, expect = (mesh.dim, 3)
    assert n == expect, ("Number of dim has changed. "
                         "Expected %d, but got %d" % (expect, n))

    n, expect = (len(mesh.periodicpointindices), 0)
    assert n == expect, ("Number of periodicpointsindices has changed. "
                         "Expected %d, but got %d" % (expect, n))

    n, expect = (mesh.numregions, 2)
    assert n == expect, ("Number of regions has changed. "
                         "Expected %d, but got %d" % (expect, n))

    n, expect = (max(max(mesh.pointsregions)), 1)
    assert n == expect, ("max(max(pointregions)) has changed. "
                         "Expected %d, but got %d" % (expect, n))

    n, expect = (min(min(mesh.pointsregions)), -1)
    assert n == expect, ("min(min(pointregions)) has changed. "
                         "Expected %d, but got %d" % (expect, n))


    # This avoids getting relative paths in the checking progress output
    os.chdir(org_dir)

def test_gmsh_1_0_import_gzipped():
    #py.test will pass on any command line arguments to the code it tests.
    #This will confuse nmag (as it doesn't know how to handle py.test's '-k'
    #and '--verbose' switches, etc.
    #
    #We thus manually delete all other entries that the name of the executable
    #from sys.argv.
    import sys

    proper_sysargv = sys.argv
    sys.argv = sys.argv[0:1]

    #work out in which directory the data files are
    org_dir = os.getcwd()
    os.chdir(os.path.split(__file__)[0])

    os.system('make sphere2.nmesh &> test_stdoutstderr3.log')

    import nmesh
    mesh = nmesh.load('sphere2.nmesh')

    assert len(mesh.points) == 258, "Something went wrong with nmeshimport --gmesh of gzipped mesh"

    os.chdir(org_dir)
