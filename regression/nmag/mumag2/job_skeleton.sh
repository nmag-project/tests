#!/bin/bash

BASEDIR=/rhome/franchin/nsim

# Run 2 subjobs simultaneously on a single node, in seperate directories

# set default resource requirements for job

#PBS -l nodes=1:ppn=2

#PBS -l walltime=4:00:00

. /rhome/franchin/nsim/exports.bash

# set names of job directories
job_dir=$BASEDIR/nsim/ocaml/unittests/nmag/mumag2

# Run 2 subjobs (this version assumes the same executable)
cd $job_dir
export PATH=$PATH:$BASEDIR/nsim/ocaml/bin
. $BASEDIR/exports.bash
LOG=__logbasename__
nsim mumag2.py __d1__ &> $LOG".1.log" &
nsim mumag2.py __d2__ &> $LOG".2.log" &

# wait for both subjobs to finish
wait
