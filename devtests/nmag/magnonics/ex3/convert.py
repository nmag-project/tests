import math

gamma = 2.210173e5 # m/A s
exch_coupling = 13.0e-12 # J/m
Msat = 0.86e6 # in A/m
mu0 = 4.0e-7*math.pi # N/A^2 = J/m A^2
C = 2*exch_coupling/(mu0*Msat) # A m

def func1(x): return gamma*C*x*x # 1/s
def func2(x): return 0.5*gamma*Msat + func2(x)
def GHz(x): return x*1e9

f = open("rec-space2.dat", "r")
content = f.read()
f.close()

f2 = open("data.dat", "w")

lines = content.splitlines()
for line in lines:
    cols = [float(ci) for ci in line.split()]
    if len(cols) > 0:
      omega = cols[0]
      k = cols[1]*1e9
      intensity = cols[4]
      if abs(func1(k) - omega) < 2e11:
          #cols[4] = 3e-8
          print "Setting curve at k=%s, omega=%s" % (k, omega)
      f2.write(" ".join([str(ci) for ci in cols]) + "\n")

    else:
      f2.write(line + "\n")

f2.close()

