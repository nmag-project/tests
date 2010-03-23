#!/bin/bash

JOB_SKELETON=job_skeleton.sh
JOB_BASENAME=job_
d_VALUES="1,6 7,8 9,10"
i=0
for d in $d_VALUES; do
  d1=$(echo $d | cut -d ',' -f 1)
  d2=$(echo $d | cut -d ',' -f 2)
  JOB_FILE=$JOB_BASENAME$i.sh
  i=$[ $i+1 ]
  sed \
    -e "s/__d1__/$d1/g" \
    -e "s/__d2__/$d2/g" \
    -e "s/__logbasename__/$JOB_FILE/g" \
    $JOB_SKELETON > $JOB_FILE
  qsub -l walltime=4:00:00 $JOB_FILE
done
