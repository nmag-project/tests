# One dimensional magnetic system studied using nsim
import os, sys, math
import nmag, nfem
from nmag import SI, mesh
from nsim import sets
from nsim.si_units.si import mu0, Tesla, degrees_per_ns
import nmeshlib.unidmesher as unidmesher

#--------------------------------------------
#--- Details about the layers and the mesh and the material

# Choose Co as a material
mat_Co = nmag.MagMaterial(
            name="Co",
            Ms=SI(1.42444e6, "A/m"),
            exchange_coupling=SI(3.02e-11, "J/m"),
            anisotropy=
              nmag.uniaxial_anisotropy(
                axis=[1, 1, 1],
                K1=SI(0.7e6,  "J/m^3"),
                K2=SI(0.18e6, "J/m^3")),
            llg_gamma_G=SI(0.2211e6, "m/ A s"),
            llg_normalisationfactor=SI(0.001e12, "1/s"))

mesh_name = "uniaxial_1d"
mesh_unit = SI(1e-9, "m")
layers = [(-10.0, 10.0)]
discretization = 1.0
new_mesh = True

#--------------------------------------------
## The initial configuration and how the applied field should change

m0 = [1, 0, 1] # Initial direction for the magnetisation

# From the norms and the direction (which is constant) we derive
# all the values that the applied field will take during the simulation
Hs = sets.vector_set(direction=[1, -2, 3],
                     norm_list=[-3.0, [200], 3.0],
                     units=SI(1e6, "A/m"))

#--------------------------------------------
## Here we set up the simulation

# Create the simulation object
sim = nmag.Simulation("uniaxial_1d", do_demag=False)

# Creates the mesh from the layer structure
mesh_file_name = '%s.nmesh' % mesh_name
if not os.path.exists(mesh_file_name) or new_mesh:
  print "Creating the mesh"
  mesh_lists = unidmesher.mesh_1d(layers, discretization)
  unidmesher.write_mesh(mesh_lists, out=mesh_file_name)

# Load the mesh
if os.path.exists(mesh_file_name):
    materials = [("Co", mat_Co)]
    sim.load_mesh(mesh_file_name, materials, unit_length=SI(1e-9, "m"))
else:
    raise StandardError,"Need file %s" % mesh_file

sim.set_m(m0) # Set the initial magnetisation

# Set additional parameters for the time-integration
#sim.set_timestepper_params(stopping_dm_dt=1*degrees_per_ns)

#--------------------------------------------
## Run the simulation to calculate the hysteresis loop

from nsim.when import every, at
sim.hysteresis(Hs,
               save=[('averages', at('convergence'))],
               convergence_check=every(5, 'step'))
