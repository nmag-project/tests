DIR=../../../..
BIN=$(DIR)/bin
NSIM=$(BIN)/nsim
NCOL=$(NSIM) $(BIN)/ncol

.PHONY: all

all: hloop.dat

run_dat.h5: run.py
	$(NSIM) run.py --clean

hloop.dat: run_dat.h5
	$(NCOL) run H_ext_0 H_ext_1 H_ext_2 m_Fe3O4_0 m_Fe3O4_1 m_Fe3O4_2 m_CoFe2O4_0 m_CoFe2O4_1 m_CoFe2O4_2 > hloop.dat

