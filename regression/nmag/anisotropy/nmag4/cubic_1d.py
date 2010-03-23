# One dimensional magnetic system studied using nsim
import os, sys, math
import nmag, nfem
from nmag import SI, mesh
from nsim import sets
from nsim.si_units.si import mu0, degrees_per_ns
import nmeshlib.unidmesher as unidmesher

#--------------------------------------------
#--- Details about the layers and the mesh and the material

# Choose Ni as a material (at temperature T=4.2 K)
mat_Ni = nmag.MagMaterial(
            name="Ni",
            Ms=SI(0.493380e6, "A/m"),
            exchange_coupling=SI(7.2e-12, "J/m"),
            anisotropy=
              nmag.cubic_anisotropy(
                axis1=[1, 1, 1],
                axis2=[2, -1, -1],
                K1=SI(-12.0e5, "J/m^3"),
                K2=SI(3.0e5, "J/m^3")),
            llg_gamma_G=SI(0.2211e6, "m/A s"),
            llg_normalisationfactor=SI(0.001e12, "1/s")
          )

mesh_name = "cubic_1d"
mesh_unit = SI(1e-9, "m")
layers = [(-10.0, 10.0)]
discretization = 0.5
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
sim = nmag.Simulation("cubic_1d", do_demag=False)

# Creates the mesh from the layer structure
mesh_file_name = '%s.nmesh' % mesh_name
if not os.path.exists(mesh_file_name) or new_mesh:
  print "Creating the mesh"
  mesh_lists = unidmesher.mesh_1d(layers, discretization)
  unidmesher.write_mesh(mesh_lists, out=mesh_file_name)

# Load the mesh
if os.path.exists(mesh_file_name):
    materials = [("Ni", mat_Ni)]
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
