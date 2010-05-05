NSIM_ROOT=../../../..
NSIM=$(NSIM_ROOT)/bin/nsim
NMESHPP=$(NSIM) $(NSIM_ROOT)/bin/nmeshpp
EXAMESH=$(NSIM_ROOT)/utils/cubicmesh/examesh

nanowire.nmesh.h5:
	$(EXAMESH) nanowire.nmesh,1000.0:433,100.0:50,2.0:1
	$(NMESHPP) -c nanowire.nmesh nanowire.nmesh.h5
	rm -f nanowire.nmesh

