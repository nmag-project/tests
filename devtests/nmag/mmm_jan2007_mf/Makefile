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

run: pre_dyn_dat.ndt

hloop_dat.ndt: hloop.py
	$(NSIM) hloop.py --clean

hloop.dat: hloop_dat.ndt
	$(NCOL) hloop_dat.ndt H_ext_0 H_ext_1 H_ext_2 M_Fe2_0 M_Fe2_1 M_Fe2_2 M_Dy_0 M_Dy_1 M_Dy_2 > hloop.dat

pre_dyn_dat.ndt: dyn.py
	$(NSIM) dyn.py --clean

pre_dyn.dat: pre_dyn_dat.ndt
	$(NCOL) pre_dyn_dat.ndt H_ext_0 H_ext_1 H_ext_2 M_Fe2_0 M_Fe2_1 M_Fe2_2 M_Dy_0 M_Dy_1 M_Dy_2 > pre_dyn.dat

dyn.dat: dyn_dat.ndt
	ncol dyn time H_ext_0 H_ext_1 H_ext_2 M_Fe2_0 M_Fe2_1 M_Fe2_2 M_Dy_0 M_Dy_1 M_Dy_2 > dyn.dat

clean:
	rm -f m_configs
