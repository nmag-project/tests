import os, sys

result_eps = "results.eps"
result_png = "results.png"

if len(sys.argv) == 1:
    files_to_process = [x for x in os.listdir('.') if x.endswith(".dat")]
else:
    files_to_process = sys.argv[1:]

try:
    import string
    import numpy
    import pylab

except:
    print "pylab is not installed. Trying with gnuplot..."
    import commands

    make_plot_gnp = "make_plot.gnp"
    f = open(make_plot_gnp, "w")
    f_content = (
        'set term postscript eps enhanced color solid\n'
        'set xlabel "time (ps)"\n'
        'set ylabel "<M> (10^6 A/m)"\n'
        'set out "%s"\n' % result_eps 
    )

    for i, dat_file in enumerate(files_to_process):
        lw = (len(files_to_process) - i)*3
        #f_content += 'set linestyle %d lt %d lw %f\n' % (i+1, i+1, lw)
 	# ^^^ works on older Gnuplot versions
	f_content += 'set style line %d lt %d lw %f\n' % (i+1, i+1, lw)

    sep = ' \\\n'
    f_content += 'plot [] []'
    for i, dat_file in enumerate(files_to_process):
        t = dat_file.replace('_', ' ')
        f_content += ('%s "%s" u ($1/1e-12):($2/1e6) t "%s: x" w l ls %d'
                      % (sep, dat_file, t, i+1))
        sep = ', \\\n'
        f_content += ('%s "%s" u ($1/1e-12):($3/1e6) t "%s: y" w l ls %d'
                      % (sep, dat_file, t, i+1))
        f_content += ('%s "%s" u ($1/1e-12):($4/1e6) t "%s: z" w l ls %d'
                      % (sep, dat_file, t, i+1))
    
    f_content += (
        '\n\nset term png\n'
        'set out "%s"\n'
        'replot\n' % result_png
    )

    f.write(f_content)
    f.close()

    print commands.getoutput('gnuplot %s' % make_plot_gnp)
    sys.exit(0)

for i,fname in enumerate(files_to_process):
    linewidth = len(files_to_process)-i
    print "working on %s" % fname
    alldatastr = map(string.split,open(fname).readlines())
    alldata = []
    for row in alldatastr:
        if row[0][0] == "#":
            print "Skipping line: ", row
            continue #skip lines starting with #
        datarow = map(float,row)
        alldata.append(datarow)
    alldata = numpy.array(alldata)
    row,cols = alldata.shape
    t = alldata[:,0]

    plotdata = []
    for c in range(1,cols):
        pylab.plot(t,alldata[:,c],label="%s %d" % (fname,c),linewidth=linewidth)

    print "data in %s has %s entries" % (fname, str(alldata.shape))

pylab.legend()
pylab.xlabel('time [s]')
pylab.ylabel('Magnetisation [A/m]')
pylab.savefig(result_eps)
pylab.savefig(result_png)



    
