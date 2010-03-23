include ../msat.inc

NSIM=../../../../../bin/nsim
NCOL=../../../../../bin/ncol


.PHONY: all ACA ACA+ Interpolation HCAI HCAII clean

all:
	make ACA
	make ACA+
	make Interpolation
	make HCAI
	make HCAII

ACA:
	make clean
	time $(NSIM) bigbar.py ACA | tee outputACA.txt
	$(NSIM) $(NCOL) bigbar_dat.ndt 0 M_Py_0 M_Py_1 M_Py_2 > ../results/nmag4_M_ACA.dat

ACA+:
	make clean
	time $(NSIM) bigbar.py ACA+ | tee outputACA+.txt
	$(NSIM) $(NCOL) bigbar_dat.ndt 0 M_Py_0 M_Py_1 M_Py_2 > ../results/nmag4_M_ACA+.dat

Interpolation:
	make clean
	time $(NSIM) bigbar.py Interpolation | tee outputInterpolation.txt
	$(NSIM) $(NCOL) bigbar_dat.ndt 0 M_Py_0 M_Py_1 M_Py_2 > ../results/nmag4_M_Interpolation.dat

HCAI:
	make clean
	time $(NSIM) bigbar.py HCAI | tee outputHCAI.txt
	$(NSIM) $(NCOL) bigbar_dat.ndt 0 M_Py_0 M_Py_1 M_Py_2 > ../results/nmag4_M_HCAI.dat

HCAII:
	make clean
	time $(NSIM) bigbar.py HCAII | tee outputHCAII.txt
	$(NSIM) $(NCOL) bigbar_dat.ndt 0 M_Py_0 M_Py_1 M_Py_2 > ../results/nmag4_M_HCAII.dat

clean:
	rm -fv bigbar_dat.ndt
	rm -fv bigbar_dat.h5
	rm -fv outputACA.txt
	rm -fv outputACA+.txt
	rm -fv outputInterpolation.txt
	rm -fv outputHCAI.txt
	rm -fv outputHCAII.txt
	rm -fv bigbar_ocaml.conf
	rm -fv bigbar_nmag.conf

