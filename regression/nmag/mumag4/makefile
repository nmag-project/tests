.PHONY: run all clean relax field1 field2

ROOT=../../../..
CUBICMESH=$(ROOT)/utils/cubicmesh/cubicmesh
EXAMESH=$(ROOT)/utils/cubicmesh/examesh
NSIM=$(ROOT)/bin/nsim
NMESHPP=$(ROOT)/bin/nmeshpp

all: relax field1 field2

sp4.nmesh.h5:
	#$(CUBICMESH) sp4.nmesh,500.0:50,125.0:12,3.0:1
	#$(CUBICMESH) sp4.nmesh,500.0:200,125.0:50,3.0:1
	$(EXAMESH) sp4.nmesh,500:170,125:60,3:2
	$(NMESHPP) -c sp4.nmesh sp4.nmesh.h5
	rm -f sp4.nmesh

relax: sp4.nmesh.h5
	$(NSIM) run.py --clean relax

field1:
	$(NSIM) run.py --clean field1

field2:
	$(NSIM) run.py --clean field2

clean:
	rm -f m0.h5 sp4.nmesh.h5 field1_* field2_* relaxation_*

