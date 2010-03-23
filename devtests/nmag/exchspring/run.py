# One dimensional magnetic system studied using nsim
import os, sys, math
import nmag, nfem
from nmag import SI, mesh
from nsim import sets
from nsim.si_units.si import mu0, degrees_per_ns
import nmeshlib.unidmesher as unidmesher

#--------------------------------------------
#--- Details about the layers and the mesh and the material

mesh_unit = SI(1e-9, "m")
layers = [(-20.0, 20.0)]
discretization = 0.5
new_mesh = True

#--------------------------------------------
## The initial configuration and how the applied field should change

m0 = [0, 0, 1] # Initial direction for the magnetisation

H_direction = [0.01, 0.01, -1] # The direction of the applied field
#The list of values taken by the norm of the applied field
H_norms = [0.01, 0.2, 0.4, [], 4.0]
H_unit = SI(1e6, "A/m") # The unit for these values

# From the norms and the direction (which is constant) we derive
# all the values that the applied field will take during the simulation
Hs = sets.vector_set(direction=H_direction, norm_list=H_norms, units=H_unit)

#--------------------------------------------
## Here we set up the simulation

# Create the material
mat = nmag.MagMaterial(
        name="Py",
        Ms=SI(0.86e6, "A/m"),
        exchange_coupling=SI(13.0e-12, "J/m"),
        llg_damping=SI(0.5))

# Create the simulation object
sim = nmag.Simulation("1d", do_demag=False)

# Creates the mesh from the layer structure
mesh_file_name = 'run.nmesh'
if not os.path.exists(mesh_file_name) or new_mesh:
  print "Creating the mesh"
  mesh_lists = unidmesher.mesh_1d(layers, discretization)
  unidmesher.write_mesh(mesh_lists, out=mesh_file_name)

# Load the mesh
if os.path.exists(mesh_file_name):
    sim.load_mesh(mesh_file_name, [("Py", mat)], unit_length=SI(1e-9, "m"))
else:
    raise StandardError,"Need file %s" % mesh_file

sim.set_m(m0) # Set the initial magnetisation

def pinning(r):
    if (abs(r[0]) >= 9.99e-9): return 0.0
    return 1.0

sim.set_pinning(pinning)

# Set additional parameters for the time-integration
sim.set_params(stopping_dm_dt=1*degrees_per_ns,
               ts_rel_tol=1e-6, ts_abs_tol=1e-6)

#--------------------------------------------
## Run the simulation to calculate the hysteresis loop

from nsim.when import every, at
sim.hysteresis(Hs,
               save=[('averages', 'fields', at('convergence'))],
               convergence_check=every(5, 'step'))
