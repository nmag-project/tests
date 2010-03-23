#!/bin/sh

FREQ_FILE=$1
t=`tail -n 1 $FREQ_FILE | cut -d ' ' -f 1`
f0=`tail -n 1 $FREQ_FILE | cut -d ' ' -f 2`
t0=`echo $t*2.0/3.0 | bc -l`

cat << EOF > fit.gnp
r = 1/$t
f0 = $f0
delta_f = -f0 
f(t) = f0 + delta_f*exp(-r*t)
t0 = 1000
set fit errorvariables
fit [$t0:] f(x) "$FREQ_FILE" u 1:2 via f0, delta_f, r
plot "$FREQ_FILE" u 1:2 w l, f(x)
pause -1
set print "-"
print f0, ",", f0_err
EOF

FREQ_AND_ERR=`gnuplot fit.gnp 2>/dev/null`
FREQ=`echo $FREQ_AND_ERR | cut -d , -f 1`
ERR=`echo $FREQ_AND_ERR | cut -d , -f 2`

echo "corrected from $f0 to $FREQ +- $ERR"

