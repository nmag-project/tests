import os
from mesh_gen import mesh_filename_list
from nsim.setup import nsim_exec_path

out_filename = "perf.dat"

for mesh_filename in mesh_filename_list:
    os.system("%s bigbar.py %s %s --clean"
              % (nsim_exec_path, mesh_filename, out_filename))

