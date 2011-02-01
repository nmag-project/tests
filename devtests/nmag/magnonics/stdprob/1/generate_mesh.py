import commands
import nsim.setup

size = [1000, 50, 1]
num_cells = [None, 25, 1]

num_cells[0] = int(round(0.5 * 3**0.5 * size[0]*num_cells[1]/float(size[1])))

nmesh_file = "nanowire.nmesh"
h5_file = "nanowire.nmesh.h5"

ex = nsim.setup.get_root_path(["utils", "cubicmesh", "examesh"])
cmnd = (ex + " " + nmesh_file + "," +
        ",".join(["%s:%s" % (size[i], num_cells[i]) for i in range(3)]))

print "Executing: " + cmnd
print commands.getoutput(cmnd)

nsimex = nsim.setup.get_exec_path()
nmeshppex = nsim.setup.get_exec_path("nmeshpp")

cmnd = "%s --nolog -- %s -c %s %s" % (nsimex, nmeshppex, nmesh_file, h5_file)
print "Executing: " + cmnd
print commands.getoutput(cmnd)

print "Removing %s" % nmesh_file
print commands.getoutput("rm " + nmesh_file)

