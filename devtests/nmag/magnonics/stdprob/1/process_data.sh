NSIM_ROOT=../../../../../../src
NSIM=$NSIM_ROOT/bin/nsim
NMAGPROBE="$NSIM -- $NSIM_ROOT/bin/nmagprobe"

$NMAGPROBE \
  --verbose par-dyn_dat.h5 --field=m_Py \
  --time=0,1000e-12,51 --space=0,1000,251/25/0 --ref-time=0.0 \
  --scalar-mode=component,2 --ft-axes=0,1 --ft-out=norm \
  --out=real-space.dat --ft-out=rec-space.dat


cat << 'EOF' > plot.gnp
set pm3d map
splot [] [0:] 'real-space.dat' u 2:($1/(2*pi*1e9)):5
pause -1

splot [] [0:] 'rec-space.dat' u 2:($1/(2*pi*1e9)):5
pause -1
EOF
gnuplot plot.gnp

