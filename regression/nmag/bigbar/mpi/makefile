include ../msat.inc

NSIM=../../../../../bin/nsim-raw
NCOL=../../../../../bin/ncol

MPICH2PATH=../../../../../../lib/mpich2/bin


.PHONY: all run results clean


clean:
	rm -fv bigbar_par_dat.ndt
	rm -fv bigbar_par_dat.h5
	rm -fv output.txt
	rm -fv bigbar_par_ocaml.conf
	rm -fv bigbar_par_nmag.conf


NMESHSORT=../../../../../bin/nmeshsort
NMESHPP=../../../../../bin/nmeshpp

mpi-sortmesh:
	$(NMESHPP) -c ../bar30_30_100.nmesh.h5 tmp.nmesh
	$(NMESHSORT) tmp.nmesh 2 bar_sorted.nmesh
	$(NMESHPP) -c bar_sorted.nmesh bar_sorted.nmesh.h5

run-mpich1:
	time mpirun -np 2 $(NSIM) bigbar_par.py --clean | tee output_mpi.txt	

results-mpich1:
	$(NCOL) bigbar_par_dat.ndt 0 M_Py_0 M_Py_1 M_Py_2 > ../results/nmag4mpi_M.dat


run-mpich2:
	$(MPICH2PATH)/mpd &
	sleep 1
	time $(MPICH2PATH)/mpiexec -n 2 $(NSIM) bigbar_par.py --clean | tee output_mpi.txt	
	$(MPICH2PATH)/mpdallexit

results-mpich2:
	$(NCOL) bigbar_par_dat.ndt 0 M_Py_0 M_Py_1 M_Py_2 > ../results/nmag4mpi_M.dat


