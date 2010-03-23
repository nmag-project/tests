NSIM=../../../../bin/nsim
NCOL=../../../../bin/ncol

MPICH2PATH=../../../../../lib/mpich2/bin

clean:
	rm -f output.txt
	rm -f make.out

mpich1-hello: clean
	mpirun -np 4 $(NSIM) mpi_hello.py > output.txt

mpich2-hello: clean
	$(MPICH2PATH)/mpd &
	sleep 1
	time $(MPICH2PATH)/mpiexec -n 4 $(NSIM) mpi_hello.py > output.txt
	$(MPICH2PATH)/mpdallexit





