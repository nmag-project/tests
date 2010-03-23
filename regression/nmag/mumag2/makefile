# generate netgen geometry specification files
geo:
	nsim meshes.py

# convert neu meshes to nmesh meshes: does not convert if the h5 file
# is already there
convert:
	NEUS=$$(find ./ -name "film*.neu") && \
	for NEU in $$NEUS; do \
	  H5=$$(basename $$NEU .neu).h5; \
	  [ -e $$H5 ] || nmeshimport --netgen $$NEU $$H5; \
	done

run:
	nsim mumag2.py

.PHONY: run_oommf

plots:
	gnuplot gen_plots.gnp

.PHONY: geo convert run plots
