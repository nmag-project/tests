#!/bin/sh

POSSIBLE_EXECS="../bin/nsim ../../src/bin/nsim"

echo "Searching for the Nsim executable..."
for EXEC in $POSSIBLE_EXECS; do
  echo "$EXEC: "
  if [ -x $EXEC ]; then
    echo "found. Using this!"
    NSIM=$EXEC
  fi
done

if [ x$NSIM = x ]; then
  echo "Nsim executable not found."
  echo "Using: nsim"
  NSIM=nsim
fi

$NSIM setup.py

