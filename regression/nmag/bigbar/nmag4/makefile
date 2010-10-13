include ../../../../config/tools.inc

include ../msat.inc

.PHONY: all run results clean

all:
	make clean
	make run
	make results

mpi:
	make mpi-clean
	make mpi-sortmesh
	make mpi-run
	make mpi-results

run:
	time $(NSIM) bigbar.py | tee output.txt	

results:
	$(NCOL) bigbar_dat.ndt 0 M_Py_0 M_Py_1 M_Py_2 > ../results/nmag4_M.dat

results_mpi:

clean:
	rm -fv bigbar_dat.ndt
	rm -fv bigbar_dat.h5
	rm -fv output.txt
	rm -fv bigbar_ocaml.conf
	rm -fv bigbar_nmag.conf

mpi-clean:
	rm -fv bigbar_par_dat.ndt
	rm -fv bigbar_par_dat.h5
	rm -fv output.txt
	rm -fv bigbar_par_ocaml.conf
	rm -fv bigbar_par_nmag.conf

mpi-sortmesh:
	$(NMESHPP) -c ../bar30_30_100.nmesh.h5 tmp.nmesh
	$(NMESHSORT) tmp.nmesh 2 bar_sorted.nmesh
	$(NMESHPP) -c bar_sorted.nmesh bar_sorted.nmesh.h5

mpi-run:
	time mpirun -np 2 $(NSIM) bigbar_par.py | tee output_mpi.txt	

mpi-results:
	$(NCOL) bigbar_par_dat.ndt 0 M_Py_0 M_Py_1 M_Py_2 > ../results/nmag4mpi_M.dat

