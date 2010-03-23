import os, sys, math
import nmag, nfem
from nmag import SI, mesh
from nsim import sets
from nsim.si_units.si import mu0, Tesla, degrees_per_ns
from nsim.when import every, at

from dyfe2_yfe2_dyfe2 import DyFe2_YFe2_DyFe2, m_file

#--------------------------------------------
## The initial configuration and how the applied field should change

# Initial direction for the magnetisation
directions = {'m_Dy':[0, 0, -1], 'm_Fe2':[0, 0, 1]}

def m0_Dy(r):
  return directions['m_Dy']

def m0_Fe(r):
  return directions['m_Fe2']

#--------------------------------------------

B_direction = [0.0, 0.0, 1.0] # The direction of the applied field

#The list of values taken by the norm of the applied field
B_unit = Tesla # The unit for these values
B_norms = [60.0, 55.0, [], 20.0, 18.0, [], 10.0, 9.5, [], 4.5, 4.25,
           4.2, 4.18, [], 3.8, 3.0, 0.0, -5.0, [], -40.0, -40.5, [], -60.0]

# From the norms and the direction (which is constant) we derive
# all the values that the applied field will take during the simulation
Hs = sets.vector_set(direction=B_direction,
                     norm_list=B_norms,
                     units=B_unit/mu0) # remember that H = B/mu0

# A small deviation to avoid points of unstable equilibrium
H_dev = [SI(0.005e6, "A/m"), SI(0.005e6, "A/m"), 0]
Hs = [[Hi+H_devi for Hi, H_devi in zip(H, H_dev)]
      for H in Hs]

#--------------------------------------------
# The system setup is done inside the module dyfe2_yfe2_dyfe2

dyfe2_yfe2_dyfe2 = DyFe2_YFe2_DyFe2("hloop", 1.0, norm_factor=0.001e12)
sim = dyfe2_yfe2_dyfe2.setup()

# Set additional parameters for the time-integration
sim.set_params(stopping_dm_dt=5*degrees_per_ns,
               ts_rel_tol=1e-5, ts_abs_tol=1e-5)

#--------------------------------------------
## Run the simulation to calculate part of the hysteresis loop

sim.set_m(m0_Fe, 'm_Fe2') # Set the initial magnetisation
sim.set_m(m0_Dy, 'm_Dy')

sim.hysteresis(Hs, save=[('averages', at('convergence'))])
