.PHONY: all clean

NMESHPP=../../../../bin/nmeshpp
MAGPARLOG2GRACE=../../../../utils/magparlog2grace.py

all: results.dat

clean:
	rm -fv run.log

bar.nmesh.h5:
	ln -s ../$@ $@

bar.inp: bar.nmesh.h5
	$(NMESHPP) $? --magpar $@

bar.log: bar.inp allopt.txt bar.krn
	rm -f bar.log
	magpar-0.7

results.dat: bar.log
	python $(MAGPARLOG2GRACE) $? --ts 1e-9 2 3 6 7 8 > $@

