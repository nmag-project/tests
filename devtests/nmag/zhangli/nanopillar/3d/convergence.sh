#!/bin/sh
DS=j*_l*
OUTDIR=convergence
mkdir -p $OUTDIR
for D in $DS; do
  echo "python convergence.py $D/freq.dat >$OUTDIR/$D.dat"
  python convergence.py $D/freq.dat >$OUTDIR/$D.dat
done

