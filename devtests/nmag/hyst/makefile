include ../../../config/tools.inc 

.PHONY: all clean

all: results.eps

$(MACHINEFILE):
	echo `hostname` >> $(MACHINEFILE)
	echo `hostname` >> $(MACHINEFILE)

bigbar.nmesh.h5: $(CUBICMESH)
	$(CUBICMESH) bigbar.nmesh,30:10,30:10,100:33
	$(NMESHPP) -c bigbar.nmesh bigbar.nmesh.h5
	rm -f bigbar.nmesh

hyst_dat.ndt: makefile hyst.py bigbar.nmesh.h5 $(MACHINEFILE)
	@read -p "How many processors? " NP && \
	echo "Running: $(MPIRUN) -np $$NP $(NSIM) hyst.py --clean &> log_bigbar.txt" && \
	$(MPIRUN) -np $$NP $(NSIM) hyst.py --clean &> log_bigbar.txt

results.dat: hyst_dat.ndt
	$(NCOL) hyst H_ext_0 H_ext_1 H_ext_2 M_Py_0 M_Py_1 M_Py_2 stage time stage_time step stage_step > $@

results.eps: results.dat
	gnuplot results.gnp

clean:
	rm -f hyst_dat.ndt

