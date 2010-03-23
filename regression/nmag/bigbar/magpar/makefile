include ../msat.inc

NMESHPP=../../../../../bin/nmeshpp
MAGPARLOG2GRACE=../../../../../utils/magparlog2grace.py

all:
	make clean
	make run
	make results

clean:
	rm -fv bigbar.log

bigbar.inp:
	$(NMESHPP) ../bar30_30_100.nmesh.h5 --magpar bigbar.inp

run:
	M_SAT_T=$$(echo "import math; print $(M_SAT)*(4*math.pi*1e-7)" | python) && \
	sed -e "s/M_SAT/$$M_SAT_T/g" bigbar.krn.orig > bigbar.krn
	make bigbar.inp
	#this line may need some fine-tuning
	magpar | tee output.txt

results:
	python $(MAGPARLOG2GRACE) bigbar.log --Ms $(M_SAT) --ts 1e-9 2 6 7 8 > ../results/magpar_M.dat
