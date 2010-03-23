#!/bin/bash
NSIM=../../../../../../bin/nsim
while true
do
  $NSIM run.py --clean &>/dev/null
  if [ $? -eq 1 ]; then
    exit 0
  fi
done

