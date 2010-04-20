import os
from mesh_gen import mesh_filename_list
from nsim.setup import nsim_exec_path


for np in range(1, 5):
    mpirun_exec_path = "mpirun -np %d" % np
    out_filename = "perf-np%d.dat" % np
    for mesh_filename in mesh_filename_list:
        os.system("%s %s bigbar.py %s %s --clean"
                  % (mpirun_exec_path, nsim_exec_path,
                     mesh_filename, out_filename))

