NMAG_ROOT=../../../../src
include ../../../tools.inc

.PHONY: all

all: memlog.dat

bar.nmesh.h5: bar.geo

memlog.dat: bar.nmesh.h5 run.py
	$(NSIM) run.py -l debug --clean --petsc-opts -malloc_info -malloc_dump -malloc_debug -info &> memlog.dat

