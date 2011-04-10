# One dimensional magnetic system studied using nsim
import os, sys, math
import nmag
from nmag import SI, mesh, vector_set
from nsim.si_units.si import mu0, degrees_per_ns
import nmeshlib.unidmesher as unidmesher

#--------------------------------------------
# We simulate a job kill if the command line contains "kill"
def simulate_kill(s):
    if "kill" in sys.argv:
        sys.exit(7)

#--------------------------------------------
#--- Details about the layers and the mesh and the material

ps = SI(1e-12, "s")

mesh_name = "1d"
mesh_unit = SI(1e-9, "m")
layers = [(-10.0, 10.0)]
discretization = 0.5
new_mesh = True

exchange_coupling = SI(13.0e-12, "J/m") # Exchange coupling constant
m_sat = SI(0.86e6, "A/m")               # Saturation magnetisation

#--------------------------------------------
## The initial configuration and how the applied field should change

m0 = [1, 0, 1] # Initial direction for the magnetisation

H_direction = [1, 1, 1] # The direction of the applied field
#The list of values taken by the norm of the applied field
H_norms = [10.0, 9.5, [], 0.0]
H_unit = SI(1e6, "A/m") # The unit for these values

# From the norms and the direction (which is constant) we derive
# all the values that the applied field will take during the simulation
Hs = vector_set(direction=H_direction, norm_list=H_norms, units=H_unit)

#--------------------------------------------
## Here we set up the simulation

# Create the material
mat_Py = nmag.MagMaterial(
           name="Py",
           Ms=m_sat,
           exchange_coupling=exchange_coupling,
           anisotropy=nmag.uniaxial_anisotropy(
                        axis=[1,0,0],
                        K1=SI(5e6, "J/m^3")),
           llg_gamma_G=SI(0.2211e6, "m/A s"),
           llg_damping=SI(0.5),
           llg_normalisationfactor=SI(0.001e12, "1/s"))

# Create the simulation object
sim = nmag.Simulation(do_demag=False)

# Creates the mesh from the layer structure
mesh_file_name = '%s.nmesh' % mesh_name
if not os.path.exists(mesh_file_name) or new_mesh:
  print "Creating the mesh"
  mesh_lists = unidmesher.mesh_1d(layers, discretization)
  unidmesher.write_mesh(mesh_lists, out=mesh_file_name)

# Load the mesh
if os.path.exists(mesh_file_name):
    sim.load_mesh(mesh_file_name, [("Py", mat_Py)], unit_length=SI(1e-9, "m"))
else:
    raise StandardError,"Need file %s" % mesh_file

sim.set_m(m0) # Set the initial magnetisation

#--------------------------------------------
## Run the simulation to calculate the hysteresis loop

from nsim.when import every, at
sim.hysteresis(Hs,
               save=[('averages', 'restart', at('convergence'))],
               do=[(simulate_kill, at('time', 105*ps))],
               convergence_check=every(5, 'step'))

