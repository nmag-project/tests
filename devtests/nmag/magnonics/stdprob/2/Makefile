include ../../../../../config/tools.inc

FILES=a_progress.txt a_relaxed.h5 a_dat.h5 a_dat.ndt relax_dat.h5 relax_dat.ndt rec-space.dat real-space.dat relax_progress.txt plot.gnp

all: run-parallel

a.geo:
	python write_geo_a.py

a.nmesh.h5: a.geo

run-parallel: a.nmesh.h5
	rm -f a_relaxed.h5
	$(NSIM) a.py --clean
	$(NSIM) a.py --clean
	mkdir -p parallel
	mv $(FILES) parallel/

