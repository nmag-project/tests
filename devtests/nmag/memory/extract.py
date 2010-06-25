import sys
f = open(sys.argv[1], "r")
ls = f.readlines()
f.close()

vmem0 = 0
rss0 = 0
for l in ls:
    if "Memory report" in l:
        cols = l.split("=")[1:]
        t, rss, vmem = [float(c.strip().split()[0]) for c in cols]
        desc = cols[-1].strip().split(" ", 2)[-1]
        print t, rss, vmem, rss - rss0, vmem - vmem0, '"%s"' % desc
        vmem0, rss0 = vmem, rss

