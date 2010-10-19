.PHONY: all_uniaxial all_cubic uniaxial cubic results_uniaxial results_cubic

include ../../../../config/tools.inc

all_uniaxial: uniaxial results_uniaxial

all_cubic: cubic results_cubic

bar.nmesh.h5: $(CUBICMESH)
	$(CUBICMESH) bar.nmesh,10.0:2,5.0:1,5.0:1
	$(NMESHPP) -c bar.nmesh bar.nmesh.h5
	rm bar.nmesh

uniaxial: bar.nmesh.h5
	$(NSIM) uniaxial_1d.py --clean

cubic: bar.nmesh.h5
	$(NSIM) cubic_1d.py --clean

results_uniaxial:
	$(NCOL) uniaxial_1d H_ext_0 H_ext_1 H_ext_2 m_Co_0 m_Co_1 m_Co_2 > ../results/uniaxial_1d_nmag5.dat

results_cubic:
	$(NCOL) cubic_1d H_ext_0 H_ext_1 H_ext_2 M_Ni_0 M_Ni_1 M_Ni_2 > ../results/cubic_1d_nmag4.dat

