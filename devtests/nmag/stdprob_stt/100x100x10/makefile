DIR=../../../../../
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
	#$(EXAMESH) stt.nmesh,100:60,100:69,10:12
	#$(EXAMESH) stt.nmesh,100:30,100:35,10:4
	$(EXAMESH) stt.nmesh,100:30,100:35,10:4
	$(NMESHPP) -c stt.nmesh stt.nmesh.h5
	rm -f stt.nmesh

cubic_stt.nmesh.h5: $(CUBICMESH)
	$(CUBICMESH) cubic_stt.nmesh,100:40,100:40,10:4
	$(NMESHPP) -c cubic_stt.nmesh cubic_stt.nmesh.h5
	rm -f cubic_stt.nmesh

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

