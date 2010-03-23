import os, sys, math
import nmag, nfem
from nmag import SI, mesh
from nsim import sets
from nsim.si_units.si import mu0, Tesla, degrees_per_ns
from nsim.when import every, at

from dyfe2_yfe2_dyfe2 import *

#--------------------------------------------
## The initial configuration and how the applied field should change

# Initial direction for the magnetisation
directions = {'m_Dy':[0, 0, -1], 'm_Fe2':[0, 0, 1]}

def m0_Dy(r):
  return directions['m_Dy']

def m0_Fe(r):
  return directions['m_Fe2']

#--------------------------------------------

B_direction = [0.0, 0.0, -1.0] # The direction of the applied field

#The list of values taken by the norm of the applied field
B_unit = Tesla # The unit for these values
B_norms = \
  sets.float_set([0.0, 0.1, [], 2.0, 2.25, [],
                  3.8, 3.82, [], 4.2, 4.25, [], 4.5, 4.6, [],
                  5.0, 5.5, [], 12.0])
selected_B_norms = \
  sets.float_set([0.0, 0.5, [], 3.5, 3.8, 3.9, 4.0, 4.1, 4.5, 5.0, [], 12.0])

delta_B = 0.01 # Tilt amplitude used to induce oscillations

tilted_B_norms = [B_norm + delta_B for B_norm in B_norms]
selected_B_norms = [B_norm + delta_B for B_norm in selected_B_norms]

# From the norms and the direction (which is constant) we derive
# all the values that the applied field will take during the simulation
Hs = sets.vector_set(direction=B_direction,
                     norm_list=B_norms,
                     units=B_unit/mu0) # remember that H = B/mu0

Hs_tilted = sets.vector_set(direction=B_direction,
                            norm_list=tilted_B_norms,
                            units=B_unit/mu0)

# A small deviation to avoid points of unstable equilibrium
H_dev = [SI(0.005e6, "A/m"), SI(0.005e6, "A/m"), 0]
Hs = [[Hi+H_devi for Hi, H_devi in zip(H, H_dev)]
      for H in Hs]
Hs_tilted = [[Hi+H_devi for Hi, H_devi in zip(H, H_dev)]
             for H in Hs_tilted]

#--------------------------------------------
## The current density for spin-torque calculations

j = [SI(4.22205e12, "A/m^2"), 0.0, 0.0]
j = [0*SI(1e12, "A/m^2"), 0.0, 0.0]

#--------------------------------------------
## Determine if we should run the pre simulation or the post simulation

# First we find what stages of the pre simulation we are interested in
i = 0
j = 1
selected_indices = []
for B_norm in tilted_B_norms:
  if i >= len(selected_B_norms): break
  selected_B_norm = selected_B_norms[i]
  #print B_norm, selected_B_norm
  if abs(B_norm - selected_B_norm) < 1e-10:
    selected_indices.append(j)
    i += 1
  j += 1

# For each of these stages we should have a file containing the configuration
pre_dyn = False
for selected_index in selected_indices:
  m_conf_file = m_file(selected_index)
  if not os.path.exists(m_conf_file):
    print "File '%s' not found."
    pre_dyn = True
    break

if len(selected_indices) < 1:
  pre_dyn = True

if pre_dyn:
  print "Doing preliminary simulation!"
  sim_name = "pre_dyn"
  damping = 0.5
  norm_factor = 0.001e12

else:
  print "Doing simulation of dynamics."
  sim_name = "dyn"
  damping = 0.02
  norm_factor = 0.001e12*1e5

#--------------------------------------------
# The system setup is done inside the module dyfe2_yfe2_dyfe2

dyfe2_yfe2_dyfe2 = DyFe2_YFe2_DyFe2(sim_name, damping,
                                    norm_factor=norm_factor)
sim = dyfe2_yfe2_dyfe2.setup()


#--------------------------------------------
## Run the simulation to calculate part of the hysteresis loop

# Function used to save one magnetisation configuration
save_m = lambda sim: sim.save_restart_file(m_file(sim.stage))

if pre_dyn:
  # Set additional parameters for the time-integration
  sim.set_params(stopping_dm_dt=5*degrees_per_ns,
                 ts_rel_tol=1e-5, ts_abs_tol=1e-5)

  sim.set_m(m0_Fe, 'm_Fe2') # Set the initial magnetisation
  sim.set_m(m0_Dy, 'm_Dy')

  sim.hysteresis(Hs_tilted,
                 save=[('averages', at('convergence')),
                       (save_m, at('convergence'))])

else:
  # Set additional parameters for the time-integration
  sim.set_params(stopping_dm_dt=0*degrees_per_ns,
                 ts_rel_tol=1e-8, ts_abs_tol=1e-7)

  def tune_run(H):
    scale = 3.95 - float(abs(H[2])*mu0/Tesla)
    if scale < 0.0:
      scale = -0.5*scale
    scale += 0.2
    max_time = 400.0/scale
    write_time = max_time/400.0
    return max_time, write_time

  #delta_H = delta_B/mu0
  #sim.set_j(j) # Set the current density
  new_Hs = []
  for selected_index in selected_indices:
    H = Hs[selected_index-1]

    # Do this run only if the corresponding file doesn't exist
    out_file = m_dyn_file([float(Hi/SI("A/m")) for Hi in H])
    if os.path.exists(out_file): continue

    # Set the initial magnetisation from file
    sim.load_m_from_h5file(m_file(selected_index))
    max_time, write_time = tune_run(H)
    new_Hs.append(H) # Note that we do not use Hs_tilted
    save = [(save_averages, at('convergence')
                          | every('stage_time', write_time*SI(1e-12, "s")))]
    do = [('do_next_stage', at('stage_time', max_time*SI(1e-12, "s")))]
    sim.hysteresis(new_Hs, save=save, do=do)
    print "going to the next stage!"
    sim.clock['stage'] += 1
