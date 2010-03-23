f1=open('a.txt','a+')
f2=open('a.txt','a+')

for i in range (100):
    f1.write('f1=%d\n ' % i)
    f1.flush()
    f2.write('f2=%d\n ' % i)
    f2.flush()


f1.close()
f2.close()

lines= open('a.txt','r').readlines()
for line in lines: print line,
