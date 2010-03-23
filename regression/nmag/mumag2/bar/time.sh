#!/bin/sh
# time command on eta seems not to accept options,
# contradicting the manual 
TMPFILE=./time.sh_removeme.log
TMPFILE2=./time.sh_removeme_exitstatus.log
STATFILE=statisics.log
ES=0
(time $*; echo "EXIT STATUS: $?" 1>&2) 3>&1 1>&2 2>&3 | tee $TMPFILE 3>&1 1>&2 2>&3
tail -n4 $TMPFILE >> $TMPFILE2
echo "------"$(date) >> $STATFILE
echo "EXECUTED COMMAND: "$* >> $STATFILE
head -n3 $TMPFILE2 >> $STATFILE
ES=$(tail -n1 $TMPFILE2 | cut -d : -f 2)
rm -f $TMPFILE $TMPFILE2
exit $ES
