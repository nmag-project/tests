include ../msat.inc

ODT_GRACE=../../../../../utils/odt_grace.py

all:
	make clean
	make run
	make results

clean:
	rm -fv *odt
	rm -fv *omf

run:
	sed -e "s/M_SAT/$(M_SAT)/g" bigbar.mif.orig > bigbar.mif
	time oommf.tcl +fg ++ oxsii bigbar.mif -exitondone 1

results:
	python $(ODT_GRACE) bigbar.odt Simulation_time Mx My Mz > ../results/oommf_M.dat
