import sys

if len(sys.argv) != 1:
  print "Usage: python repair.py filename.dat"
  sys.exit(1)

lines = sys.stdin.readlines()
old_time = None
t0 = 0.0
comment = ""
for line in lines:
  cols = line.split()
  time = float(cols[0])
  if old_time != None and time < old_time:
    t0 += old_time - time
    comment = " was %s" % time 
  old_time = time
  cols[0] = str(time + t0)
  print " ".join(cols) + comment
  comment = ""

