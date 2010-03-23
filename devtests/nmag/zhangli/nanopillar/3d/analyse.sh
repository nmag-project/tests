DS=j*_l*
for D in $DS; do
  data=$D/freq.dat
  appended=$D/freq_appended
  echo "Analysing '$data'"
  cat << EOF >plot.gnp
  plot "$D/freq.dat" u 1:2 w l
  pause -1
EOF
  j=`echo $D | cut -d _ -f 1 | tr "lj" "  "`
  l=`echo $D | cut -d _ -f 2 | tr "lj" "  "`
  if [ -e $appended ]; then
    echo "Data already appended for '$data'"

  else
    if [ -e $data ]; then
      gnuplot plot.gnp
      echo -n "Do you want to append the data for this file to freqs.dat? (y/N)"
      read -n1 answer
      echo
      if [ "$answer" == "y" ]; then
        echo $l $j `tail -n1 $data` >> freqs.dat
        touch $appended
      fi
    fi
  fi
done

echo "These machines are working on non accepted data:"
for D in $DS; do
  if [ ! -e $D/freq_appended ]; then
    host_file=$D/host
    if [ -e $host_file ]; then
      echo `cat $host_file` working on $D
    else
      echo "Unknown machine"
    fi
  fi
done

