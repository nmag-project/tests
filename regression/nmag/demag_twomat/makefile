include ../../../config/tools.inc

.PHONY: all run clean

all: clean run

bar.nmesh.h5: bar.geo

bar_oneregion.nmesh.h5: bar_oneregion.geo

run: bar.nmesh.h5 bar_oneregion.nmesh.h5
	$(NSIM) bug_ticket175.py --clean

clean:
	rm -f simulation1* simulation2* 
