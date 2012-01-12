
P = 0.4

a = 4.0*(P**0.5/(1 + P))**3

print "input: P=", P
print "output: a=", a
print "        P=", a/(2.0*(1.0 - a))
print "   lambda=", 2.0*(1.0 - a)/(1.0 - 2.0*a)
