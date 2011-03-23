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

sinclude ./config/tools.inc

.PHONY: all check checkall checkslow checkmpi checkhlib

TEST_DIRS=$(NSIM_ROOT_PATH)/interface .
NSIM_PYTEST=$(NSIM) --nolog $(PYTEST_EXEC) -- $(TEST_DIRS)

all: check

check_is_configured:
	@if [ ! -f ./config/tools.inc ]; then \
	  SEPL="-----------------------------------------------------"; \
	  echo $$SEPL; \
	  echo "You need to configure the test suite before using it."; \
	  echo "Please, read the file README for further information."; \
	  echo $$SEPL; \
	  exit 1; \
	fi

check: check_is_configured
	@echo "Testing all reasonably fast tests..."
	@echo "Skipping tests with name test_slow* test_mpi* test_hlib*".
	$(NSIM_PYTEST) -k "-test_slow -test_mpi -test_hlib"

checkslow: check_is_configured
	@echo "Running only slow tests..."
	$(NSIM_PYTEST) -k test_slow

checkmpi: check_is_configured
	@echo "Running only MPI tests..."
	$(NSIM_PYTEST) -k test_mpi

checkhlib: check_is_configured
	@echo "Running only HLib tests..."
	$(NSIM_PYTEST) -k test_hlib

checkall: check_is_configured
	@echo "Running all available tests..."
	$(NSIM_PYTEST)

