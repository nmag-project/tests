.PHONY: all run run2

NSIM=../../../bin/nsim
NCOL=../../../bin/ncol
NMESHPP=../../../bin/nmeshpp

all: result.ps

bar30_30_100.nmesh.h5:
	ln -s ../../regression/nmag/bigbar/$@ $@

bar.nmesh.h5: bar30_30_100.nmesh.h5
	ln -s bar30_30_100.nmesh.h5 $@

bar_ordered.nmesh.h5: bar.nmesh.h5 
	$(NMESHPP) --reordernodes $? $@

run_dat.h5: run.py bar_ordered.nmesh.h5
	rm -f run_cvode.log
	$(NSIM) run.py --clean

m.dat: run_dat.h5
	$(NCOL) run H_ext_0 H_ext_1 H_ext_2 m_Py_0 m_Py_1 m_Py_2 > $@

result.ps: m.dat plot.gnp
	gnuplot plot.gnp

run:
	rm -f run_dat.h5
	make run_dat.h5

run2:
	rm -f run_dat.h5
	mpirun -np 2 `pwd`/../../../bin/nsim run.py --clean

