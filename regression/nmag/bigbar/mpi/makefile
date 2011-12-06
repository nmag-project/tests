include ../../../../config/tools.inc

TIME=time

.PHONY: all run results clean

all: clean run results

clean:
	rm -fv bigbar_par_dat.ndt bigbar_par_dat.h5 output.txt \
	  bigbar_par_ocaml.conf bigbar_par_nmag.conf

run:
	$(MPD_EXEC) & \
	sleep 1; \
	$(TIME) $(MPIEXEC_EXEC) -np 2 \
	  $(NSIM) bigbar_par.py --clean | tee output_mpi.txt; \
	$(MPDALLEXIT_EXEC)

results:
	$(NCOL) bigbar_par_dat.ndt 0 M_Py_0 M_Py_1 M_Py_2 \
	  > ../results/nmag4mpi_M.dat
