# One dimensional magnetic system studied using nsim
import os, sys, math
import nmag, nfem
from nmag import SI, mesh
from nsim import sets
from nsim.si_units.si import mu0, Tesla, degrees_per_ns
import nmeshlib.unidmesher as unidmesher

#--------------------------------------------
#--- Details about the mesh and its discretization

mesh_unit = SI(1e-9, "m")
d1 = 15 # in nm (Fe3O4)
d2 = 5  # in nm (CoFe2O4)
layers = [(0.0, d1), (d1, d1+d2)]
discretization = 1.0

#--------------------------------------------
#--- Details about the layers and the materials

# First we define Fe3O4
Ms = SI(0.5e6, "A/m")

anisotropy = \
  nmag.uniaxial_anisotropy(axis=[1, 0, 0], K1=SI(0.01e6, "J/m^3"))

# demag becomes a shape anisotropy
demag = \
  nmag.uniaxial_anisotropy(axis=[1, 0, 0], K1=-0.5*mu0*Ms**2)

mat_Fe3O4 = \
  nmag.MagMaterial(name="Fe3O4",
                   Ms=Ms,
                   exchange_coupling=SI(13.0e-11, "J/m"), # ?
                   anisotropy=anisotropy+demag,
                   llg_damping=0.5)

# Then we define CoFe2O4
Ms = SI(0.4e6, "A/m")

axis = [math.sqrt(1.0/3.0), math.sqrt(2.0/3.0), 0]
anisotropy = \
  nmag.uniaxial_anisotropy(axis=axis, K1=SI(0.2e6, "J/m^3"))

demag = \
  nmag.uniaxial_anisotropy(axis=[1, 0, 0], K1=-0.5*mu0*Ms**2)

mat_CoFe2O4 = \
  nmag.MagMaterial(name="CoFe2O4",
                   Ms=Ms,
                   exchange_coupling=SI(13.0e-11, "J/m"), # ?
                   anisotropy=anisotropy+demag,
                   llg_damping=0.5)

# Here we decide how the materials are distributed on the mesh
mats = [("Fe3O4", mat_Fe3O4), ("CoFe2O4", mat_CoFe2O4)]

# Coupling between the two materials (at the surface)
Fe3O4_CoFe2O4_sup_lc = SI(-1.0e6, "N/A^2 m")

#--------------------------------------------
## The initial configuration and how the applied field should change

# Initial direction for the magnetisation
directions = {'m_Fe3O4'  :[0, 1, 0],
              'm_CoFe2O4':[0, -1, 0]}

def m0_Fe3O4(r):
  return directions['m_Fe3O4']

def m0_CoFe2O4(r):
  return directions['m_CoFe2O4']

# The direction of the applied field
B_direction = [0.0, 1.0, 0.0]

#The list of values taken by the norm of the applied field
B_norms = [-5.0, -4.9, [], 5.0]
B_unit = Tesla # The unit for these values

# From the norms and the direction (which is constant) we derive
# all the values that the applied field will take during the simulation
Hs = sets.vector_set(direction=B_direction,
                     norm_list=sets.float_set(B_norms),
                     units=B_unit/mu0) # remember that H = B/mu0

# A small deviation to avoid points of unstable equilibrium
H_dev = [SI(0.005e6, "A/m")]*3
Hs = [[Hi+H_devi for Hi, H_devi in zip(H, H_dev)]
      for H in Hs]

#--------------------------------------------
## Here we set up the simulation

# Create the simulation object
sim = nmag.Simulation("run", do_demag=False, adjust_tolerances=False)

# Set the coupling between the two magnetisations
Fe3O4_CoFe2O4_lc = Fe3O4_CoFe2O4_sup_lc*mesh_unit*discretization
sim.set_local_magnetic_coupling(mat_Fe3O4, mat_CoFe2O4, Fe3O4_CoFe2O4_lc)

# Creates the mesh from the layer structure
mesh_file_name = 'run.nmesh'
mesh_lists = unidmesher.mesh_1d(layers, discretization)
unidmesher.write_mesh(mesh_lists, out=mesh_file_name)

# Load the mesh
if os.path.exists(mesh_file_name):
    sim.load_mesh(mesh_file_name, mats, unit_length=SI(1e-9, "m"))
else:
    raise StandardError,"Need file %s" % mesh_file

# Set additional parameters for the time-integration
sim.set_params(stopping_dm_dt=1*degrees_per_ns,
               ts_rel_tol=1e-6, ts_abs_tol=1e-6)

#--------------------------------------------
## Run the simulation to calculate the hysteresis loop

sim.set_m(m0_Fe3O4,   'm_Fe3O4') # Set the initial magnetisations
sim.set_m(m0_CoFe2O4, 'm_CoFe2O4')

from nsim.when import every, at
sim.hysteresis(Hs,
               save=[('averages', at('convergence')),
                     ('fields', at('convergence'))],
               convergence_check=every(5, 'step'))
