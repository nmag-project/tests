include ../../../../../config/tools.inc

FILES=a_progress.txt a_relaxed.h5 a_dat.h5 a_dat.ndt relax_dat.h5 relax_dat.ndt rec-space.dat real-space.dat relax_progress.txt plot.gnp

all: run-parallel

a.geo:
	python write_geo_a.py

a.nmesh.h5: a.geo

run-parallel: a.nmesh.h5
	rm -f a_relaxed.h5
	$(NSIM) a.py --clean parallel
	$(NSIM) a.py --clean parallel
	mkdir -p parallel
	mv $(FILES) parallel/

run-orthogonal: a.nmesh.h5
	rm -f a_relaxed.h5
	$(NSIM) a.py --clean orthogonal
	$(NSIM) a.py --clean orthogonal
	mkdir -p orthogonal
	mv $(FILES) orthogonal/

data-parallel:
	$(NMAGPROBE) \
	  --verbose a_dat.h5 --field=m_Py \
	  --time=0,5000e-12,251 --space=0,435,30/0/0 --ref-time=0.0 \
	  --scalar-mode=component,2 --ft-axes=0,1 --ft-out=norm \
	  --out=real-space.dat --ft-out=rec-space.dat

