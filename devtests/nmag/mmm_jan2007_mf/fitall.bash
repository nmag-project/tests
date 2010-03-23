
IN_FILES=`ls -r --sort=time m_dyns/*.dat`
rm -f fits0.dat fits1.dat fits2.dat
for IN_FILE in $IN_FILES; do
  python autofit.py $IN_FILE
done
