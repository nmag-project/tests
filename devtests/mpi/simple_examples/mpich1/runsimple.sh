#!/bin/sh

echo "compiling source"
mpiCC ../simple.c -o simple

N=4
echo "writing machinefile for $N machines"

rm -f machinefile
for i in `seq 1 $N`; do
    echo "localhost" >> machinefile
done
    

export RSH=ssh
echo "executing the lot"
time mpirun -np $N -machinefile machinefile simple
