include ../../../config/tools.inc

clean:
	rm -f output.txt
	rm -f make.out

mpich1-hello: clean
	$(MPIEXEC_EXEC) -np 4 $(NSIM) mpi_hello.py > output.txt

mpich2-hello: clean
	$(MPD_EXEC) &
	sleep 1
	time $(MPIEXEC_EXEC) -n 4 $(NSIM) mpi_hello.py > output.txt
	$(MPDALLEXIT_EXEC)

