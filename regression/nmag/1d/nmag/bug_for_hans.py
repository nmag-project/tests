# One dimensional magnetic system studied using nsim
import os, sys, math
import nmag, nfem
from nmag import SI, mesh
from nsim import sets
from nsim.si_units.si import mu0, degrees_per_ns
import nmeshlib.unidmesher as unidmesher

#--------------------------------------------
#--- Details about the materials and the layers

# Create the materials
mat_Fe = nmag.MagMaterial(
           name="Fe",
           Ms=SI(0.55e6, "A/m"),
           exchange_coupling=SI(14.6e-12, "J/m"))

# Create the material
mat_Dy = nmag.MagMaterial(
           name="Dy",
           Ms=SI(1.73e6, "A/m"),
           exchange_coupling=SI(0.01e-12, "J/m"),
           anisotropy=nmag.uniaxial_anisotropy(
                        axis=[1,0,0],
                        k1=SI(5e6, "J/m^3")))

mesh_name = "1d"
mesh_unit = SI(1e-9, "m")
layers = [(-10.0, -5.0), (-5.0, 5.0), (5.0, 10.0)]
mat_allocation = [("DyFe2_up", [mat_Dy, mat_Fe]),
                  ("YFe2", mat_Fe),
                  ("DyFe2_down", [mat_Dy, mat_Fe])]
discretization = 0.5
new_mesh = True

#--------------------------------------------
## The initial configuration and how the applied field should changes

# Initial direction for the magnetisation
directions = {'m_Dy':[1,0,0], 'm_Fe':[-1,0,0]}
def m0((x,), dof_name):
  return directions[dof_name]

H_direction = [1, 1, 1] # The direction of the applied field
#The list of values taken by the norm of the applied field
H_norms = [10.0, 9.5, [], 8.0]
H_unit = SI(1e6, "A/m") # The unit for these values

# From the norms and the direction (which is constant) we derive
# all the values that the applied field will take during the simulation
Hs = sets.vector_set(direction=H_direction, norm_list=H_norms, units=H_unit)

#--------------------------------------------
## Here we set up the simulation

# Create the simulation object
sim = nmag.Simulation("dyfe2_yfe2_dyfe2", do_demag=False)

# Set the coupling between the two magnetisations
#sim.set_local_magnetic_coupling(mat_Fe, mat_Dy, SI(-2e-4, "N/A^2"))

# Creates the mesh from the layer structure
mesh_file_name = '%s.nmesh' % mesh_name
if not os.path.exists(mesh_file_name) or new_mesh:
  print "Creating the mesh"
  mesh_lists = unidmesher.mesh_1d(layers, discretization)
  unidmesher.write_mesh(mesh_lists, out=mesh_file_name)

# Load the mesh
if os.path.exists(mesh_file_name):
    sim.load_mesh(mesh_file_name, mat_allocation, unit_length=SI(1e-9, "m"))
else:
    raise StandardError,"Need file %s" % mesh_file

sim.set_m(m0) # Set the initial magnetisation

# Set additional parameters for the time-integration
sim.set_timestepper_params(stopping_dm_dt=1*degrees_per_ns,
                           rel_tolerance=1e-7, abs_tolerance=1e-7)

#--------------------------------------------
## Run the simulation to calculate the hysteresis loop

num_save = 0
def save_fields_vtk(sim):
    global num_save
    sim.save_fields_vtk("all_fields_%d.vtk" % num_save)
    num_save += 1

from nsim.when import every, at
#sim.hysteresis(Hs,
               #save=[('averages', at('convergence')),
                     #(save_fields_vtk, every(100, 'step'))],
               #convergence_check=every(5, 'step'))
sim.hysteresis(Hs,
               save=[('averages', at('convergence')),
                     ('fields', every(100, 'step'))],
               convergence_check=every(5, 'step'))
