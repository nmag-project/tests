.PHONY: all others nmag4 oommf magpar plots check clean

NSIM=../../../../bin/nsim

all:
	make nmag
	make others


remesh:
	make netgen	
	make meshconvert



remesh15:
	#This target is handy to create a mesh such that the 
	#nmag simulation of this mesh needs about 1GB at the 
	#the moment (23 July 2008)
	netgen -geofile=bar30_30_100_15.geo -meshfiletype="Neutral Format" -meshfile=bar30_30_100_15.neutral -batchmode
	nmeshimport --netgen bar30_30_100_15.neutral bar30_30_100.nmesh.h5
	gzip -f bar30_30_100_15.neutral


netgen:
	netgen -geofile=bar30_30_100.geo -meshfiletype="Neutral Format" -meshfile=bar30_30_100.neutral -batchmode


meshconvert:
	nmeshimport --netgen bar30_30_100.neutral bar30_30_100.nmesh.h5
	gzip -f bar30_30_100.neutral


others:
	make oommf
	make plots
	make magpar
	make plots

nmag4:
	cd nmag4; make all

nmag4mpi:
	cd nmag4; make mpi

oommf:
	cd oommf; make all

magpar:
	cd magpar; make all

plots:	
	cd results; ../$(NSIM) make_plot.py

check: nmag4 plots 

mpicheck: nmag4mpi plots 

clean:
	cd nmag4; make clean
	cd oommf; make clean
	cd magpar; make clean	
