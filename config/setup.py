"""This python script must be called to select the Nsim distribution which is
to be associated to the test suite.
Let's say you want to test the nsim executable "/home/user/programs/nsim",
then first call:

    cd test # enter the test suite
    /home/user/programs/nsim setup.py
    make

setup.py will bind the test suite to the particular nsim executable used to
launch it.
"""

import sys
import os
from os.path import dirname, realpath, exists, join

def which(filename, other_paths=None):
    '''Analogous of the unix ``which'': which("gcc") whill return the full
    path of the command which will be executed typing "gcc" on a shell.'''

    paths = os.environ.get("PATH", "").split(os.pathsep)
    if other_paths != None:
        paths.extend(other_paths) 

    for path in paths:
        full_filename = join(path, filename)
        if exists(full_filename):
            return realpath(full_filename)

    raise ValueError("Command '%s' not found!" % full_filename)

def trywhich(filename, other_paths=None):
    filenames = [filename] if type(filename ) == str else filename
    for filename in filenames:
        try:
            return which(filename, other_paths=other_paths)
        except ValueError:
            pass
    return None

try:
    import nsim

except:
    print("ERROR: You should launch this script using nsim, but it looks "
          "like you launched it using a normal Python interpreter.")
    sys.exit(1)

try:
    from nsim.setup import get_root_path
    from nsim.version import dist_mode

except:
    print("ERROR: This script works only with Nsim version 0.1.0 or above.")
    sys.exit(1)

my_path = os.path.split(__file__)[0]
nsim_test_path = os.path.realpath(os.path.join(my_path, os.path.pardir))
nsim_root_path = get_root_path()
nsim_bin_path = get_root_path(["bin"])

if dist_mode == None:
    sys_preferred_path = None

elif dist_mode == "all-source":
    ps = ["../bin", "../lib/mpich2/bin"]
    sys_preferred_path = [realpath(join(nsim_root_path, p))
                          for p in ps]

else:
    raise ValueError("nsim.version.dist_mode=%s: Unexpected value"
                     % repr(dist_mode))

# Now we try to locate the required executables
true_exec = which("true")
bash_exec = which("bash")
mpd_exec = trywhich("mpd", sys_preferred_path)
mpdallexit_exec = trywhich("mpdallexit", sys_preferred_path)
mpiexec_exec = trywhich(["mpirun", "mpiexec"], sys_preferred_path)
pytest_exec = which("py.test", sys_preferred_path)

print "Test root path:", nsim_test_path
print "Nsim root path:", nsim_root_path
print "Nsim bin path:", nsim_bin_path
print "Nsim dist mode:", dist_mode
print
print "System preferred path:", sys_preferred_path
print "mpd executable:", mpd_exec
print "mpdallexit executable:", mpdallexit_exec
print "mpiexec executable:", mpiexec_exec
print "py.test executable:", pytest_exec
print "path to bash:", bash_exec

toolfile_in_name = "tools.inc.in"
toolfile_name = "tools.inc"

f = open(toolfile_in_name, "r")
content = f.read()
f.close()

f = open(toolfile_name, "w")
substs = [("$NSIM_TEST_PATH$", nsim_test_path),
          ("$NSIM_BIN_PATH$", nsim_bin_path),
          ("$NSIM_ROOT_PATH$", nsim_root_path),
          ("$MPD_EXEC$", mpd_exec),
          ("$MPDALLEXIT_EXEC$", mpdallexit_exec),
          ("$MPIEXEC_EXEC$", mpiexec_exec),
          ("$PYTEST_EXEC$", pytest_exec),
	  ("$BASH_EXEC$", bash_exec) ]
for src, dest in substs:
    content = content.replace(src, dest or true_exec)
f.write(content)
f.close()

