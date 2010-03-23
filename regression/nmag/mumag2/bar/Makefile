.PHONY: run_oommf run_magpar extract plot

LOCAL_PATH=${PWD}
MAIN_PATH=$(LOCAL_PATH)/../../../../
NSIM=$(MAIN_PATH)/bin/nsim
NCOL=$(MAIN_PATH)/bin/ncol
ODTGRACE=$(MAIN_PATH)/utils/odt_grace.py
MP2GRACE=mp2grace
OOMMF=oommf.tcl
TIME=$(LOCAL_PATH)/time.sh
SIM_NAME=bar

run_oommf:
	$(NSIM) specification.py
	(cd oommf && rm -f $(SIM_NAME).odt && $(TIME) $(OOMMF) +fg ++ oxsii $(SIM_NAME).mif -exitondone 1)
	$(ODTGRACE) oommf/$(SIM_NAME).odt Bx By Bz Mx My Mz > results/oommf.dat

run_nmag:
	rm -f nmag/specification.py && \
	 ln -s ${PWD}/specification.py nmag/specification.py
	cd nmag && $(TIME) $(NSIM) $(SIM_NAME).py --clean && cd ..
	$(NCOL) nmag/$(SIM_NAME) 11 12 13 8 9 10 > results/nmag.dat

run_magpar:
	$(NSIM) specification.py
	rm -rf specification*.conf specification*.log
	cd magpar && rm -f $(SIM_NAME).log && $(TIME) magpar && \
	 $(MP2GRACE) 5 6 7 8 9 10 > ../results/magpar.dat && cd ..

results/plot.gnp: results/plot.gnp.orig
	$(NSIM) specification.py
	rm -rf specification*.conf specification*.log

extract:
	$(ODTGRACE) oommf/$(SIM_NAME).odt Bx By Bz Mx My Mz > results/oommf.dat
	$(NCOL) nmag/$(SIM_NAME) 11 12 13 8 9 10 > results/nmag.dat
	(cd magpar && $(MP2GRACE) 5 6 7 8 9 10 > ../results/magpar.dat)

plot: results/plot.gnp
	cd results && gnuplot plot.gnp && cd ..
