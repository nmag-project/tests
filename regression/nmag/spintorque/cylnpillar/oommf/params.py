from nsim.si_units import SI, si
from math import pi

soft_width=40.0
hard_width=5.0

L     = SI(40e-9, "m")               # length  of the exchange spring
alpha = SI(0.02)                     # damping
Ms    = SI(0.54861229676e6, "A/m")   # A/m (moment density of iron in YFe2
A     = SI(14.6e-12, "J/m")          # Exchange coupling constant of iron in YFe2
Pj    = SI(0.1e12, "A/m^2")          # Polarized current density
xi    = SI(0.01)                     # Adiabaticity parameter

mu_0  = si.mu0                       # magnetic permeability of free space
mu_b  = si.bohr_magneton
e     = si.positron_charge
gamma = SI(2.210173e5, "m/A s")/(1+alpha*alpha)


bj = Pj*mu_b/(e*Ms*(1 + xi*xi))
print "u    =", bj
print "beta =", xi

import sys
sys.exit(0)

a = 1 + alpha*xi
v = mu_b*Pj/(e*Ms*(1 + xi*xi))
vv = v/(1 + alpha*alpha)
freq = vv/(2*alpha*L)
print "Uncorrected frequency is", freq

freq /= m_ort
print "Current in strange units", vv
print "Frequency is", freq

#theta = 180.0*(1-exp(k*(0.5*L-x)))/(1 - exp(k*L))

"""
plot \
  "my_final_m.dat" u 3:(atan2($7, $8)/pi*180) t "phi", \
  "my_final_m.dat" u 3:(acos($6)/pi*180) t "theta", \
  theta(x*1e-9)
pause -1
"""
