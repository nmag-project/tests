#!/bin/bash
j_off=0
j_on=6
l=0
ls="0 1 2 3 4 5 6 7 8 9 10"
jobs_per_node=1

if [ $# -lt 1 ]; then
  my_ls=""
  for l in $ls; do
    jobdir="j$j_on""_l$l"
    if [ ! -e $jobdir/job_done ]; then
      if [ $jobs_per_node -gt 0 ]; then
        my_ls="$my_ls $l"
        jobs_per_node=$[ $jobs_per_node - 1 ]
      fi
    fi
  done

  if [ "$my_ls" == "" ]; then
    exit 1 # When all jobs are finished
  fi

  echo "This node with deal with l=$my_ls"
  sleep 2
  for l in $my_ls; do
    sh run.sh $l
  done
  exit 0

else
  l=$1
fi

jobdir="j$j_on""_l$l"
echo "Working inside $jobdir"
[ -e $jobdir/job_done ] && exit 0
rm -rf $jobdir
mkdir $jobdir
cd $jobdir
touch job_done

ln -s ../esigar.py .
nsim esigar.py $j_off $l --clean
(cd m_esigar && ln -s 1.h5 2.h5 && ln -s 1.h5 last.h5)
nsim esigar.py $j_on $l --clean
