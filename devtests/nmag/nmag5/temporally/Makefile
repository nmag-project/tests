include ../../../../config/tools.inc

.PHONY: run

all: run mz.dat plot.eps

run:
	[ -f relaxed.h5 ] || $(NSIM) run.py --clean
	$(NSIM) run.py --clean

mz.dat:
	$(NCOL) dyn time m_Py_2 > mz.dat

plot.eps: plot.gnp mz.dat
	gnuplot plot

plot.pdf: plot.eps
	epstopdf plot.eps

clean:
	rm -f relaxed.h5 mz.dat
