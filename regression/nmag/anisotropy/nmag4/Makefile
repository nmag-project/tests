.PHONY: all_uniaxial all_cubic uniaxial cubic results_uniaxial results_cubic

NSIM=../../../../../bin/nsim
NCOL=../../../../../bin/ncol

all_uniaxial: uniaxial results_uniaxial

all_cubic: cubic results_cubic

uniaxial:
	$(NSIM) uniaxial_1d.py --clean

cubic:
	$(NSIM) cubic_1d.py --clean

results_uniaxial:
	$(NCOL) uniaxial_1d H_ext_0 H_ext_1 H_ext_2 M_Co_0 M_Co_1 M_Co_2 > ../results/uniaxial_1d_nmag4.dat

results_cubic:
	$(NCOL) cubic_1d H_ext_0 H_ext_1 H_ext_2 M_Ni_0 M_Ni_1 M_Ni_2 > ../results/cubic_1d_nmag4.dat

