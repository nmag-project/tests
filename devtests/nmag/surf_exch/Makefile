ROOT=../../
UTILS=$(ROOT)/utils
BIN=$(ROOT)/bin
CUBICMESH=$(UTILS)/cubicmesh/cubicmesh
NMESHPP=$(BIN)/nmeshpp

mesh.nmesh.h5:
	$(CUBICMESH) mesh.nmesh,64.0:32,10.0:5,10.0:5 x:10.0,30.0,34.0,54.0
	$(NMESHPP) -c mesh.nmesh mesh.nmesh.h5
	rm -f mesh.nmesh

