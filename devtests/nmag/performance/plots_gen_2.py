from nsim.setup import get_exec_path
from mesh_gen import get_meshinfo
import os

filename_in = "perf.dat"
filename = "perf-ext.dat"
gnuplot_filename = "plot.gnp"

# Get mesh info from the file
meshinfo = get_meshinfo()

import glob
filenames = glob.glob("sec-*.dat")
filenames.sort()

src = ""
for filename in filenames:
    src += """
plot "$FILENAME$" u 3:4:1 t "" w l lc variable, \
     "" u 3:4:2 t "" with labels font "Helvetica,8", x t ""
pause -1
""".replace("$FILENAME$", filename)

f = open("plot_2.gnp", "w")
f.write(src)
f.close()
