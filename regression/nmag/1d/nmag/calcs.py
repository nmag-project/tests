import os, sys, math
from nmag import SI, mesh
from nsim import sets
from nsim.si_units.si import *

gamma = SI(2.210173e5, "m/(A*s)")
csi = 0.01
polarisation = 1
damping = 0.02

Hb0 = bending_field = 4.25*T/mu0 # bending field (current j = 0)
exchange_coupling_Fe2 = SI(14.6e-12, "J/m")
Ms_Fe2 = SI(0.54861229676e6, "A/m")
C_Fe2 = 2*exchange_coupling_Fe2/(mu0*Ms_Fe2)

e = positron_charge
mu_b = bohr_magneton
gilbert_to_ll = 1.0/(1 + damping*damping)

beta = gilbert_to_ll*(polarisation*mu_b / (e*Ms_Fe2*(1 + csi*csi)))

c_P = beta*(csi - damping)/gamma
c_D = beta*(1 + damping*csi)/(damping*gamma)

spring_length = math.pi*(C_Fe2/bending_field)**0.5

delta_H = 1.0*T/mu0
Hb = Hb0 - delta_H # bending field (with current j > 0)

# Current required to decrease the bending field from Hb0 to Hb (by delta_H)
j = (C_Fe2/Hb0)**0.5 * delta_H/abs(c_P)

print "the exchange spring length is %s" % spring_length
print "the current necessary to decrease Hb by %s is %s" % (delta_H, j)

j = SI(1e12, "A/m^2")

gilbert_to_ll = 1.0/(1 + damping*damping)
beta = gilbert_to_ll*(polarisation*mu_b / (e*Ms_Fe2*(1 + csi*csi)))
c_D = beta*(1 + damping*csi)/(damping*gamma)
Hb = Hb0 - abs(j*c_P*math.pi)/spring_length

print "Bending field when current j = 0 is %f T" % float(Hb0*mu0/T)
print "Bending field when current j = %s is %f T" % (j, float(Hb*mu0/T))
print "Velocity of free spin-waves for j = %s is %s" % (j, -beta*(1 + csi*damping)*j)
