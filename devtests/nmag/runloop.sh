#!/bin/bash

while true
do
  sh run.sh
  if [ $? -eq 1 ]; then
    exit 0
  fi
done

