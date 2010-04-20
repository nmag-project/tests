# Copyright (C) 2010 University of Southampton
#  by Matteo Franchin
#
# This file is intended to be included in the Makefile of the Nmag examples.
# Before including this file, you should define the NMAG_ROOT variable.
# Finally, it should look like that:
#
# NMAG_ROOT=../..
# include $(NMAG_ROOT)/tests/tools.inc

# Make sure we use always the Bash shell
SHELL=/bin/bash

# Nmag tools
BIN_PATH=$(NMAG_ROOT)/bin
NSIM=$(BIN_PATH)/nsim
NSIM_RAW=$(BIN_PATH)/nsim-raw
NMAGPP=$(NSIM_RAW) $(BIN_PATH)/nmagpp
NCOL=$(NSIM_RAW) $(BIN_PATH)/ncol
NMESHIMPORT=$(NSIM_RAW) $(BIN_PATH)/nmeshimport
NMESHPP=$(NSIM_RAW) $(BIN_PATH)/nmeshpp
NMAGPROBE=$(NSIM_RAW) $(BIN_PATH)/nmagprobe

# External tools
NETGEN=/usr/bin/netgen
GNUPLOT=/usr/bin/gnuplot

# Make NEU from GEO file
%.neu: %.geo
	$(NETGEN) -geofile=$< -moderate -meshfiletype="Neutral Format" -meshfile=$@ -batchmode

# Make NMESH from NEU
%.nmesh.h5: %.neu
	$(NMESHIMPORT) --netgen $< $@

# Make directly NMESH from GEO
%.nmesh.h5: %.geo
	BN=`basename $<` && \
	$(NETGEN) -geofile=$< -moderate -meshfiletype="Neutral Format" \
	  -meshfile=$$BN.neu -batchmode && \
	$(NMESHIMPORT) --netgen $$BN.neu $@ && \
	rm -f $$BN.neu

