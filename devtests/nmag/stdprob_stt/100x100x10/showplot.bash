#!/bin/bash

DATADIR=results
HAMDATA=hamburg_100x100x10.dat
PLOTFILE=$DATADIR/plot.gnp
ST="w l"
[ ! -d $DATADIR ] && mkdir -p $DATADIR

echo -n 'plot "../'$HAMDATA'" u 1:2 '$ST' 1, "../'$HAMDATA'" u 1:3 t "" '$ST' 1, "../'$HAMDATA'" u 1:4 t "" '$ST' 1,' > $PLOTFILE

DIRS=maxrod*
COMMA=""
N=2
for DIR in $DIRS; do
  OUT=$DIR.dat
  SAVE_DIR=`pwd`
  echo "Entering $DIR"
  cd $DIR
  if [ -f stt_dat.ndt ]; then
    ncol stt time M_Py_0 M_Py_1 M_Py_2 > ../$DATADIR/$OUT
    cd $SAVE_DIR
    echo $COMMA'\' >> $PLOTFILE
    echo -n '"'$OUT'"' u 1:2 $ST $N, '"'$OUT'"'' u 1:3 t "" '$ST $N, '"'$OUT'"'' u 1:4 t "" '$ST $N >> $PLOTFILE
    N=$[ $N + 1 ]
    COMMA=", "
  fi
  cd $SAVE_DIR
done
echo  >> $PLOTFILE
echo pause -1 >> $PLOTFILE
cd $DATADIR
gnuplot plot.gnp

