include ../../../config/tools.inc

all: mpi-hello

clean:
	rm -f output.txt
	rm -f make.out

mpi-hello: clean
	$(MPD_EXEC) &
	sleep 1
	time $(MPIEXEC_EXEC) -n 4 $(NSIM) mpi_hello.py > output.txt
	$(MPDALLEXIT_EXEC)

unknown-hello: mpi-hello
