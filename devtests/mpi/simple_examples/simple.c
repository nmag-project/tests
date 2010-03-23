#include <mpi.h> 
#include<stdlib.h>
#include<stdio.h>

/* Also include usual header files */ 
main(int argc, char **argv) {

  int my_rank, size;
	  
  MPI_Init (&argc, &argv); 

  MPI_Comm_size( MPI_COMM_WORLD, &size ); 
  MPI_Comm_rank( MPI_COMM_WORLD, &my_rank );
  
  printf("I am %d out of %d\n", my_rank, size);

  /* Terminate MPI */ 
  MPI_Barrier( MPI_COMM_WORLD );
  MPI_Finalize (); 
  exit (0);
}

