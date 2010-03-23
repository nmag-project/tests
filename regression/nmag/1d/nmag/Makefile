.PHONY: run clean results

NSIM=../../../../../bin/nsim
NCOL=../../../../../bin/ncol

run:
	rm -f 1d_dat.*
	$(NSIM) 1d.py

clean:
	rm -f 1d_*.*

results:
	$(NCOL) 1d H_ext_0 H_ext_1 H_ext_2 m_Py_0 m_Py_1 m_Py_2 > ../results/nmag.dat
