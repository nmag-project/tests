# Nmag micromagnetic simulator
# Copyright (C) 2011 University of Southampton
# Hans Fangohr, Thomas Fischbacher, Matteo Franchin and others
#
# WEB:     http://nmag.soton.ac.uk
# CONTACT: nmag@soton.ac.uk
#
# AUTHOR(S) OF THIS FILE: Matteo Franchin
# LICENSE: GNU General Public License 2.0
#          (see <http://www.gnu.org/licenses/>)

include ./config/tools.inc

.PHONY: all

all:
	$(NSIM) --nolog $(PYTEST_EXEC) -- -k "-test_slow -test_mpi -test_hlib"

