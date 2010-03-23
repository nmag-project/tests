NSIM_ROOT=../../../../..
NSIM=$NSIM_ROOT/bin/nsim.ng
NMAGPROBE="$NSIM -- $NSIM_ROOT/bin/nmagprobe"

$NMAGPROBE \
  --verbose dyn_dat.h5 --field=m_Py \
  --time=0,100e-12,101 --space=0,400,201/2/2 --ref-time=0.0 \
  --scalar-mode=component,1 --ft-axes=0,1 \
  --out=real-space.dat --ft-out=rec-space.dat


cat << 'EOF' > plot.gnp
set pm3d map
splot [] [0:] 'real-space.dat' u 2:($1/(2*pi*1e9)):5
pause -1

splot [] [0:] 'rec-space.dat' u 2:($1/(2*pi*1e9)):5
pause -1
EOF
gnuplot plot.gnp

