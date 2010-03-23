#!/bin/sh

MPICH2PATH=/usr/local/mpich2/bin

echo "compiling source"
/usr/local/mpich2/bin/mpicc  -I/usr/local/mpich2/include  ../simple.c -osimple

N=4
    
$MPICH2PATH/mpd &
$MPICH2PATH/mpdtrace &
$MPICH2PATH/mpiexec -l -n $N ./simple
$MPICH2PATH/mpdallexit
