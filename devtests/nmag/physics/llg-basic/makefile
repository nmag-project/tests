# Copyright (C) 2010 University of Southampton

NMAG_ROOT=../../../../../src
include ../../../../tools.inc

.PHONY: all mesh run force plot clean clean-all

# Standard targets

all: plot

mesh: mesh.nmesh.h5

run: nmag4.dat model.dat

force:
	rm -f run_dat.ndt
	$(MAKE) all

plot: plot.eps

mesh.nmesh.h5: mesh.geo

nmag4.dat: nmag4.py mesh.nmesh.h5
	$(NSIM) nmag4.py --clean
	$(NCOL) nmag4 time m_Py_0 m_Py_1 m_Py_2 > nmag4.dat

model.dat: model.py mesh.nmesh.h5
	$(NSIM) model.py

plot.eps: plot.gnp nmag4.dat model.dat
	$(GNUPLOT) plot.gnp

clean:
	rm -f ng.ini run_log.log.old run_progress.txt run_restart.h5 test.out

clean-all: clean
	rm -f mesh.nmesh.h5 plot.eps run.dat run_dat.h5 run_dat.ndt
