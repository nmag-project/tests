"""This python script must be called to select the Nsim distribution which is
to be associated to the test suite.
Let's say you want to test the nsim executable "/home/user/programs/nsim",
then first call:

    cd test # enter the test suite
    /home/user/programs/nsim setup.py
    make

setup.py will bound the test suite to the particular nsim executable used to
launch it.
"""

import sys
import os
from os.path import dirname, realpath, exists, join

try:
    import nsim

except:
    print("ERROR: You should launch this script using nsim, but it looks "
          "like you launched it using a normal Python interpreter.")
    sys.exit(1)


try:
    from nsim.setup import get_root_path

except:
    print("ERROR: This script works only with Nsim version 0.1.0 or above.")
    sys.exit(1)

nsim_bin_path = get_root_path(["bin"])

print "Nsim bin path:", nsim_bin_path

toolfile_in_name = "tools.inc.in"
toolfile_name = "tools.inc"

f = open(toolfile_in_name, "r")
content = f.read()
f.close()

f = open(toolfile_name, "w")
f.write(content.replace("$NSIM_BIN_PATH$", nsim_bin_path))
f.close()

