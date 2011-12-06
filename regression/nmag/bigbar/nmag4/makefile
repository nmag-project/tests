include ../../../../config/tools.inc

TIME=time

.PHONY: all run results clean

all: clean run results

mpi: mpi-clean mpi-sortmesh mpi-run mpi-results

run:
	$(TIME) $(NSIM) bigbar.py | tee output.txt	

results:
	$(NCOL) bigbar_dat.ndt 0 M_Py_0 M_Py_1 M_Py_2 > ../results/nmag4_M.dat

clean:
	rm -fv bigbar_dat.ndt bigbar_dat.h5 output.txt bigbar_ocaml.conf \
	  bigbar_nmag.conf

mpi-run:
	$(TIME) mpirun -np 2 $(NSIM) bigbar_par.py | tee output_mpi.txt	

mpi-results:
	$(NCOL) bigbar_par_dat.ndt 0 M_Py_0 M_Py_1 M_Py_2 \
	  > ../results/nmag4mpi_M.dat

mpi-clean:
	rm -fv bigbar_par_dat.ndt bigbar_par_dat.h5 output.txt \
	  bigbar_par_ocaml.conf bigbar_par_nmag.conf
