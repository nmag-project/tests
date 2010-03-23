# The bar in the following figure depicts our exchange spring:
#
#    [1][  2  ][1][  2  ][1]
#
# Material 1 si the hard material (DyFe2)
# Material 2 is the soft material (YFe2)

import math
import nfem
from nfem.euler import *
from nfem.mumag import *
import Numeric, os, sys
import nmesh.unidmesher as unidmesher
from nfem.save_field import save_field

#--------------------------------------------
#--- Details about the layers and the mesh
mesh_name = "dyfe2_yfe2"

hard_layer_width = 5.0
soft_layer_width = 10.0
first_layer_is_hard = True
number_of_layers = 3

discretization = 0.5
new_mesh = True

#--- The damping used for the fast and realistic stages
damping_fast = 0.5
damping_real = 0.02

#--- Other details about the simulation
initial_h_ext = [0.005, 0.0, 0.005]
final_h_ext = [0.005, 8.0, 0.005]
num_stages = 160
# List of external fields (one for each stage)
# We use Tesla here: we will convert to 10^6 A/m later
delta_h = 0.05
h_ext_list = from_to(initial_h_ext, final_h_ext, num_stages)

#--- What to save and when:
save_mean_mags_every_step = -1
one_file_per_stage = False
save_mags_every_step = -1
save_mags_every_stage = True

#--- The directory where the program runs
run_directory = 'run_nsim_dyfe2_yfe2/'

#--------------------------------------------
## Creates the (h_ext, damping) list

# In general we want to do the following: go to the starting point h_ext
# with a big damping parameter, then move by delta_h to the point h_ext+delta_h
# using the realistic value for the damping. Therefore we create a list
# of (h_ext, damping): 'h_ext' will be reached using 'damping'!
h_ext_and_damping_list = []
h = [x1-x0 for x0, x1 in zip(initial_h_ext, final_h_ext)]
h_norm = math.sqrt( sum([x*x for x in h]) )
for h_ext in h_ext_list:
  dh_norm = delta_h/h_norm
  dh = [dh_norm*x for x in h]
  h_ext_plus_delta_h = [x + dx for x, dx in zip(h_ext, dh)]
  h_ext_and_damping_list.append( (h_ext, damping_fast) )
  #h_ext_and_damping_list.append( (h_ext_plus_delta_h, damping_real) )

#--------------------------------------------
## Creates the layer structure
layers = []
all_layers = []
all_hard_layers = []
all_soft_layers = []
volume = 0.0
volume_hard = 0.0
layer_is_hard = first_layer_is_hard
x = last_x = 0.0
for i in range(1, number_of_layers+1):
  all_layers.append( i )
  if layer_is_hard:
    width = hard_layer_width
    all_hard_layers.append( i )
    x += hard_layer_width
    volume_hard += hard_layer_width
  else:
    width = soft_layer_width
    all_soft_layers.append( i )
    x += soft_layer_width

  layers.append( [last_x, x] )
  volume += x - last_x
  last_x = x
  layer_is_hard = not layer_is_hard

#--------------------------------------------
## Creates the mesh from the layer structure
mesh_file_name = run_directory+'%s.nmesh' % mesh_name
if not os.path.exists(mesh_file_name) or new_mesh:
  print "Creating the mesh"
  mesh_lists = unidmesher.mesh_1d(layers, discretization)
  unidmesher.write_mesh(mesh_lists, out=mesh_file_name)

print "Loading the mesh"
mesh = nmesh.load(mesh_file_name)

#--------------------------------------------
## Setups the simulation

# Generic factors used to convert between different units
mu0 = 4.0*math.pi/10.0 # This is expressed in simulation units 10^(-6) N/A^2
tesla_to_ApM = 1.0/mu0

#--------------------------------------------
## Setup the simulation objects

ms_fe = 0.54861229676
ms_dy = 1.18085121013+ms_fe # Just taken from Jurgen's exSpringMaker...

s = Eulers(mesh=mesh)

s_fe = s.Euler(where=all_layers, initial_mag=[0.0, -1.0, 0.0], m_sat=ms_fe)
s_fe.set(include_exchange=True, exchange_coupling=14.6)
s_fe.set(external_field=[0.0, 0.0, 0.0], calculate_energy=True)

s_dy = s.Euler(where=all_hard_layers, initial_mag=[0.0, 1.0, 0.0], m_sat=ms_dy)
s_dy.set(external_field=[0.0, 0.0, 0.0], calculate_energy=True)

# Anisotropy of the Dysprosium layers
s_dy.add_cubic_anis(axis1=[0.7071, 0.0, -0.7071], axis2=[0.7071, 0.0, 0.7071],
  k1= 33.853774961, k2=-16.1710504363, k3= 16.3584237059)

# The demagnetising field act as a shape anisotropy in the 1D model:
# a term H_demag = -M_x which can be expressed as an uniaxial anisotropy
#   H_demag = (2 K_1 m*u) / (mu0*M_sat)
# where the axis u = (1, 0, 0) and K_1 = -mu0*M_sat/2
s_fe.add_uniaxial_anis(axis=[1.0, 0.0, 0.0], k1=-0.5*mu0*ms_fe*ms_fe)
s_dy.add_uniaxial_anis(axis=[1.0, 0.0, 0.0], k1=-0.5*mu0*ms_dy*ms_dy)

# Set exchange coupling between Dy and Fe moments in the DyFe2 layers
s.exchange_coupling( couple=(s_dy, s_fe), exchange_coupling=-223.37 )

# We tune the integrator: the default settings are not acceptable for
# small damping parameters such as 0.02
s_fe.set(absolute_step_error=0.349e-3, relative_step_error=0.002, stopping_dm_dt=1.7e-6)
s_dy.set(absolute_step_error=0.349e-3, relative_step_error=0.002, stopping_dm_dt=1.7e-6)
s.setup()

# The time-itegrator

#--------------------------------------------
## The proper simulation starts...

m_fe = s_fe.get_field("m")
m_dy = s_dy.get_field("m")
htot = s_fe.get_field("h_total")
save_m_fe = save_field(m_fe, "m", run_directory+"m_fe.dat")
save_m_dy = save_field(m_dy, "m", run_directory+"m_dy.dat")
save_htot = save_field(htot, "h_total", run_directory+"htot.dat")

# This function save the mean magnetisations
file_all = None
file_fe = None
file_dy = None
def save_mean_mags(h_ext, create_new_files=False, close_files=False):
  global file_all, file_fe, file_dy
  hx, hy, hz = h_ext
  file_missing = file_all==None or file_fe==None or file_dy==None
  if create_new_files or file_missing:
    if file_missing:
      suffix = ".dat"
    else:
      suffix = "_%.2f_%.2f_%.2f.dat" % (hx, hy, hz)
    file_all = open(run_directory+"mm"+suffix , "w")
    file_fe = open(run_directory+"mm_fe"+suffix, "w")
    file_dy = open(run_directory+"mm_dy"+suffix, "w")
    first_line = "# Stage %d: h_ext(Tesla) = %f, %f, %f\n" % (num_stage, hx, hy, hz)
    file_all.write(first_line)
    file_fe.write(first_line)
    file_dy.write(first_line)
  elif close_files:
    file_all.close()
    file_dy.close()
    file_fe.close()
  else:
    # Save the mean magnetisations
    mm_fe = nfem.integrate_field(m_fe, "m")
    mm_dy = nfem.integrate_field(m_dy, "m")
    mm_dy = Numeric.array(mm_dy[0][1])
    mm_fe = Numeric.array(mm_fe[0][1])
    mm = (ms_dy*mm_dy + ms_fe*mm_fe) / volume
    total_energy = s_dy.total_energy()
    mx, my, mz = mm
    file_all.write( "%f %f %f %f %g %g %g %f %d %g\n" % (s.time, hx, hy, hz, \
    mx, my, mz, total_energy, s.nr_iterations, s.old_dt) )
    file_all.flush()
    mm_fe = mm_fe * (ms_fe / volume)
    mm_dy = mm_dy * (ms_dy / volume_hard)
    mx, my, mz = mm_fe
    file_fe.write( "%f %f %f %f\n" % (s.time, mx, my, mz) )
    mx, my, mz = mm_dy
    file_dy.write( "%f %f %f %f\n" % (s.time, mx, my, mz) )

def save_mags():
  # Save the entire fields
  save_m_fe(time=s.time)
  save_m_dy(time=s.time)
  save_htot(time=s.time)

num_stage = 0
for h_ext, damping in h_ext_and_damping_list:
  num_stage += 1
  h_ext_tesla = [h*tesla_to_ApM for h in h_ext]
  hx, hy, hz = h_ext

  s_dy.damping = damping
  s_fe.damping = damping
  s.next_stage(h_ext=h_ext_tesla)

  while not s_fe.is_converged:
    if not s.advance(): break
    if s.every(save_mean_mags_every_step): save_mean_mags(h_ext)
    if s.every(save_mags_every_step): save_mags()

  save_mean_mags(h_ext, create_new_files=one_file_per_stage)
  if save_mags_every_stage: save_mags()

  if s_fe.is_converged:
    status = "converged"
  else:
    status = "not converged"
  print "stage for field =", h_ext, ", status =", status

save_m_fe(close=True)
save_m_dy(close=True)
save_htot(close=True)
save_mean_mags(None, close_files=True)
