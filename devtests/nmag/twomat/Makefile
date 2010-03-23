BASE=../../../..
BIN=$(BASE)/bin
NSIM=$(BIN)/nsim
NCOL=$(BIN)/ncol

NAME=dyfe2_yfe2_dyfe2
SCRIPT=$(NAME).py
NDT=$(NAME)_dat.ndt
LOOP_DAT=hyst_loop.dat
LOOP_EPS=hyst_loop.eps
DATA_DIR=m_$(NAME)

run: $(LOOP_EPS)

$(NDT): $(SCRIPT)
	rm -rf $(DATA_DIR)
	$(NSIM)	$(SCRIPT) --clean

$(LOOP_DAT): $(NDT)
	$(NCOL) $(NDT) H_ext_0 H_ext_1 H_ext_2 M_Fe2_0 M_Fe2_1 M_Fe2_2 M_Dy_0 M_Dy_1 M_Dy_2 > $@

$(LOOP_EPS): $(LOOP_DAT) hyst_loop.gnp
	gnuplot hyst_loop.gnp

clean:
	rm -f $(NAME)_*.log *.old $(NAME)_log.conf $(NAME)_log.log \
	      $(NAME)_nmag.conf $(NAME)_ocaml.conf $(NAME)_progress.txt

