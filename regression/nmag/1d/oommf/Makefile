.PHONY: all clean run results

all: run

clean:
	rm -fv *.odt *.omf

run:
	rm -f 1d.odt
	time oommf.tcl +fg ++ oxsii 1d.mif -exitondone 1

results:
	odt_grace.py 1d.odt Bx By Bz Mx My Mz > ../results/oommf.dat
