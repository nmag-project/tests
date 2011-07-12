include ../../../config/tools.inc

.PHONY: all clean check

all:
	$(MAKE) clean check
	$(MAKE) clean

check: real-space.dat
	$(NSIM) run.py check

run_dat.h5:
	$(NSIM) run.py run

real-space.dat: run_dat.h5
	$(NMAGPROBE) --verbose run_dat.h5 --field=H_ext_ \
	  --time=0 --space=-10,10,11/-8,8,9/-6,6,6 \
	  --out=tmp.dat
	cat tmp.dat | tr "[]" "  " > real-space.dat
	rm tmp.dat

clean:
	rm -f real-space.dat run_dat.h5 run_dat.h5.old  run_dat.ndt \
	   run_dat.ndt.old run_log.log run_log.log.old *.pyc

