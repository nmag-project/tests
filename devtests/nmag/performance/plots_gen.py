from nsim.setup import get_exec_path
import os

filename_in = "perf.dat"
filename = "perf-ext.dat"
gnuplot_filename = "plot.gnp"
meshinfo_filename = "mesh.info"

nmeshpp_exec = get_exec_path('nmeshpp')

# We need to know how many nodes each mesh has
# This info is stored in a file which we read.
# If the file is not there, we generate it!
if not os.path.exists(meshinfo_filename):
    from mesh_gen import mesh_filename_list
    import commands
    col_num_points = []
    for mesh_filename in mesh_filename_list:
        out = commands.getoutput("%s -i %s" % (nmeshpp_exec, mesh_filename))
        lines = out.splitlines()
        for line in out.splitlines():
            if line.endswith("points"):
                num_points = line.split()[0]
        col_num_points.append(num_points)

    f = open(meshinfo_filename, "w")
    for entry in col_num_points:
        f.write("%s\n" % entry)
    f.close()

def tonum(x):
    try:
        return int(x)
    except:
        return float(x)

# Read mesh info from the file
f = open(meshinfo_filename, "r")
lines_left = f.read().splitlines()
f.close()

# Read timing data
f = open(filename_in, "r")
lines_right = f.read().splitlines()[1:]
f.close()
print lines_left, lines_right

lines = [line_left + " " + line_right
         for line_left, line_right in zip(lines_left, lines_right)]

# Write the timings data complemented with the column "nodes per mesh"
f = open(filename, "w")
f.write("\n".join(lines) + "\n")
f.close()

# Now write the Gnuplot file to plot the data
row0 = [tonum(x) for x in lines[0].split()]

src = ""
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


