DIR=../../../../
CUBICMESH_DIR=$(DIR)/utils/cubicmesh
CUBICMESH=$(CUBICMESH_DIR)/cubicmesh
EXAMESH=$(CUBICMESH_DIR)/examesh
NMESHPP=$(DIR)/bin/nmeshpp
NSIM=$(DIR)/bin/nsim
NCOL=$(DIR)/bin/ncol

.PHONY: all clean

all: results.eps

$(EXAMESH):
	(cd $(CUBICMESH_DIR) && make)

$(CUBICMESH):
	(cd $(CUBICMESH_DIR) && make)

stt.nmesh.h5: $(EXAMESH)
	# subdivision is: n x m x k, where m = n*2/sqrt(3) 
	$(EXAMESH) stt.nmesh,200:70,200:81,20:7
	$(NMESHPP) -c stt.nmesh stt.nmesh.h5
	rm -f stt.nmesh

relax_restart.h5: stt.nmesh.h5
	rm -f relax_restart.h5
	$(NSIM) stt.py --clean &> log_relax.txt

stt_dat.ndt: relax_restart.h5
	$(NSIM) stt.py --clean &> log_stt.txt

results.dat: stt_dat.ndt
	$(NCOL) $? time M_Py_0 M_Py_1 M_Py_2 > $@

results.eps: results.dat
	gnuplot results.gnp

clean:
	rm -f stt.nmesh.h5 relax_restart.h5

