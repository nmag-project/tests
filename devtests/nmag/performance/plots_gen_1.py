from nsim.setup import get_exec_path
from mesh_gen import get_meshinfo
import os

filename_in = "perf.dat"
filename = "perf-ext.dat"
gnuplot_filename = "plot.gnp"

nmeshpp_exec = get_exec_path('nmeshpp')

# Get mesh info from the file
lines_left = get_meshinfo()

def tonum(x):
    try:
        return int(x)
    except:
        return float(x)

# Read timing data
f = open(filename_in, "r")
lines_right = f.read().splitlines()[1:]
f.close()
print lines_left, lines_right

lines = [line_left + " " + line_right
         for line_left, line_right in zip(lines_left, lines_right)]

# Write the timings data complemented with the column "nodes per mesh"
f = open(filename, "w")
f.write("\n".join(lines))
# Now write the Gnuplot file to plot the data
row0 = [tonum(x) for x in lines[0].split()]

for i, col in enumerate(row0):
    src += 'col%d = %s\n' % (i + 1, col)

src += (
'''
set key left

plot \
     "perf-ext.dat" u 1:( $2/ col2) t "initialisation" w lp, \
                 "" u 1:( $4/ col4) t "simloop" w lp, \
                 "" u 1:( $6/ col6) t "advance_time" w lp, \
                 "" u 1:( $8/ col8) t "writing averages"  w lp, \
                 "" u 1:($10/col10) t "writing fields" w lp, \
                 "" u 1:($12/col12) t "num steps" w lp
pause -1
''')

f = open(gnuplot_filename, "w")
f.write(src)
f.close()
os.system("gnuplot %s" % gnuplot_filename)


