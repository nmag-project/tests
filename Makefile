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

.PHONY: all check checkall checkslow checkmpi checkhlib

NSIM_PYTEST=$(NSIM) --nolog $(PYTEST_EXEC) --

all: check
	$(NSIM) --nolog $(PYTEST_EXEC) -- -k "-test_slow -test_mpi -test_hlib"

check:
	@echo "Testing all reasonably fast tests..."
	@echo "Skipping tests with name test_slow* test_mpi* test_hlib*".
	$(NSIM_PYTEST) -k "-test_slow -test_mpi -test_hlib"

checkslow:
	@echo "Running only slow tests..."
	$(NSIM_PYTEST) -k test_slow

checkmpi:
	@echo "Running only MPI tests..."
	$(NSIM_PYTEST) -k test_mpi

checkhlib:
	@echo "Running only HLib tests..."
	$(NSIM_PYTEST) -k test_hlib

checkall:
	@echo "Running all available tests..."
	$(NSIM_PYTEST)

