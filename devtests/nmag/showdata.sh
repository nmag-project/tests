#!/bin/bash

files="freq_j014*"
for file in $files; do
  gnpfile="$file.gnp"
  cat << EOF >$gnpfile
  plot "$file" u 1:2 w lp, "$file" u 1:3 w lp
  pause -1
EOF
  gnuplot $gnpfile
  rm $gnpfile
done

