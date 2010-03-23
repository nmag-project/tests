NSIM=../../../../../bin/nsim

all: data.dat

run_dat.h5: run.py
	$(NSIM) run.py --clean

data.dat: run_dat.h5
	$(NSIM) readh5.py run_dat.h5 m Py '0,1000e-12,1001' '50,350,151/0/2' data.dat

