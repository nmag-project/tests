include ../../../../config/tools.inc

.PHONY: all mesh clean

all: mesh

mesh: periodic.nmesh.h5 full.nmesh.h5

piece.nmesh.h5: piece.geo

periodic.nmesh.h5: piece.nmesh.h5
	$(NMESHPP) -c piece.nmesh.h5 piece.nmesh
	$(NMESHMIRROR) piece.nmesh 1e-6 1e-6 1,0,0 periodic.nmesh
	$(NMESHPP) -c periodic.nmesh periodic.nmesh.h5
	rm piece.nmesh periodic.nmesh

full.nmesh.h5: full.geo

clean:
	rm -f piece.nmesh.h5 piece.nmesh periodic.nmesh.h5

