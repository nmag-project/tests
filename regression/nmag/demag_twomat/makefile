.PHONY: init init_rm

ROOT_DIR=../../../..
BIN_DIR=$(ROOT_DIR)/bin
NSIM=$(BIN_DIR)/nsim
NETGEN=netgen
NMESHIMPORT=$(BIN_DIR)/nmeshimport

bar.nmesh.h5:
	$(NETGEN) -geofile=bar.geo -meshfiletype="Neutral Format" -meshfile=bar.neu -batchmode
	$(NMESHIMPORT) --netgen bar.neu bar.nmesh.h5
	rm -f bar.neu

bar_oneregion.nmesh.h5:
	$(NETGEN) -geofile=bar_oneregion.geo -meshfiletype="Neutral Format" -meshfile=bar_oneregion.neu -batchmode
	$(NMESHIMPORT) --netgen bar_oneregion.neu bar_oneregionn.nmesh.h5
	rm -f bar.neu


init_rm:
	rm -f simulation1* simulation2* 

init: bar.nmesh.h5 bar_oneregion.nmesh.h5

