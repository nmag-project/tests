NMAG_ROOT=../../../../src
NSIM=$(NMAG_ROOT)/bin/nsim
NSIM_RAW=$(NMAG_ROOT)/bin/nsim-raw
NMESHPP=$(NSIM_RAW) $(NMAG_ROOT)/bin/nmeshpp

.PHONY: all run

all: run

bar.nmesh.h5:
	(cd $(NMAG_ROOT)/utils/cubicmesh && make) && \
	  $(NMAG_ROOT)/utils/cubicmesh/examesh bar.nmesh,100.0:20,30.0:7,30.0:10 && \
	  $(NMESHPP) -c bar.nmesh bar.nmesh.h5 && rm bar.nmesh

run: bar.nmesh.h5
	$(NSIM) run.py --clean

