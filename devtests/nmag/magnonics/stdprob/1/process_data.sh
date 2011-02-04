NSIM_ROOT=../../../../../../src
NSIM=$NSIM_ROOT/bin/nsim
NMAGPROBE="$NSIM -- $NSIM_ROOT/bin/nmagprobe"

PREFIX=$1

if [ x$PREFIX == xpar ]; then
    COMP=y
elif [ x$PREFIX == xorty ]; then
    COMP=x
elif [ x$PREFIX == xortz ]; then
    COMP=x
else
    echo "Choose either par, orty or ortz"
    exit 1
fi

$NMAGPROBE \
  --verbose $PREFIX-dyn_dat.h5 --field=m_Py \
  --time=10e-12,500e-12,25 --space=0,1000,251/25/0.5 --ref-time=0.0 \
  --scalar-mode=component,$COMP --ft-axes=x,t --ft-out=norm \
  --out=$PREFIX-real-space.dat --ft-out=$PREFIX-rec-space.dat


cat << EOF > $PREFIX-plot.gnp
set pm3d map
splot [] [0:] '$PREFIX-real-space.dat' u 2:(\$1/(2*pi*1e9)):5
pause -1

splot [] [0:] '$PREFIX-rec-space.dat' u 2:(\$1/(2*pi*1e9)):5
pause -1
EOF
gnuplot $PREFIX-plot.gnp

