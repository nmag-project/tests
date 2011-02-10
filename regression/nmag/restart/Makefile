include ../../../config/tools.inc

.PHONY: all run clean

all: run

run:
	rm -f out1.txt out2.txt
	$(NSIM) restart_1d.py --clean kill; \
		if [ $$? == 7 ]; then true; else false; fi
	$(NCOL) restart_1d stage >out1.txt
	$(NSIM) restart_1d.py --restart
	$(NCOL) restart_1d stage >out2.txt

clean:
	rm -f 1d.nmesh  out.txt restart_1d_progress.txt test_restart_log.log \
	      restart_1d_dat.ndt make.log restart_1d_dat.ndt.old restart_1d_restart.h5 \
	      out1.txt  restart_1d_log.log test_restart_1d_log.log out2.txt  \
              restart_1d_log.log.old
