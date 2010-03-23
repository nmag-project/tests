.PHONY: all run_nmag run_oommf clean_nmag clean_oommf clean results

all: run_nmag results

run_nmag:
	(cd nmag && make run results)

run_oommf:
	(cd oommf && make run results)

clean_nmag:
	(cd nmag && make clean)

clean_oommf:
	(cd oommf && make clean)

clean: clean_nmag clean_oommf

results/nmag.dat: nmag/1d.py
	make run_nmag

results/oommf.dat: oommf/1d.mif
	make run_oommf

results: results/nmag.dat results/oommf.dat
	cd results && gnuplot plot.gnp

