NMAG_ROOT=../../../../src
include ../../../tools.inc

.PHONY: all

all: plot

bar.nmesh.h5: bar.geo

memlog.dat: bar.nmesh.h5 run.py
	$(NSIM) run.py -l debug --clean --petsc-opts -malloc_info -malloc_dump -malloc_debug -info &> memlog.dat

plot.dat: memlog.dat extract.py
	python extract.py memlog.dat > plot.dat

plot: plot.dat
	gnuplot plot.gnp

clean:
	rm -f bar.nmesh.h5 memlog.dat run_dat.h5 run_dat.ndt run_log.log

