NMAG_ROOT=../../../../src
include ../../../tools.inc

.PHONY: all

all: plot

bar.nmesh.h5: bar.geo

memlog.dat: bar.nmesh.h5 run.py
	$(NSIM) run.py -l debug --clean --petsc-opts -malloc_info -malloc_dump -malloc_debug -info &> memlog.dat

results.dat: run_dat.ndt
	$(NCOL) run_dat.ndt time m_Py_0 m_Py_1 m_Py_2 > results.dat

plot.dat: memlog.dat extract.py
	python extract.py memlog.dat > plot.dat

plot: plot.dat results.dat
	gnuplot plot.gnp

clean:
	rm -f bar.nmesh.h5 memlog.dat run_dat.h5 run_dat.ndt run_log.log

re:
	mv memlog.dat memlog.dat.old || true
	$(MAKE) all

