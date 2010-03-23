BIN=../../../../bin
NSIM=$(BIN)/nsim
NCOl=$(NSIM) $(BIN)/ncol

run.dat: run.py
	$(NSIM) run.py --clean

analytic.dat: analytic
	./analytic

analytic: analytic.c
	gcc `pkg-config gsl --libs` analytic.c -o analytic


