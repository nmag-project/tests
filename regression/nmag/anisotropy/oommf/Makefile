.PHONY: all_uniaxial all_cubic uniaxial cubic results_uniaxial results_cubic

ODT_GRACE=../../../../../utils/odt_grace.py

all_uniaxial: uniaxial results_uniaxial

all_cubic: cubic results_cubic

uniaxial: clean
	time oommf.tcl +fg ++ oxsii uniaxial_1d.mif -exitondone 1

cubic:
	time oommf.tcl +fg ++ oxsii cubic_1d.mif -exitondone 1

results_uniaxial:
	$(ODT_GRACE) uniaxial_1d.odt Bx By Bz Mx My Mz > ../results/uniaxial_1d_oommf.dat

results_cubic:
	$(ODT_GRACE) cubic_1d.odt Bx By Bz Mx My Mz > ../results/cubic_1d_oommf.dat

clean:
	rm -fv *odt
	rm -fv *omf
