# One dimensional magnetic system studied using nsim
import math
from nmag import vector_set, SI
import nmag.nmag5 as nmag
from nsim.si_units.si import mu0, Tesla, degrees_per_ns

#--------------------------------------------
#--- Details about the layers and the mesh and the material

# Choose Co as a material
anisotropy = \
  nmag.uniaxial_anisotropy(axis=[(1.0/3)**0.5, (1.0/3)**0.5, (1.0/3)**0.5],
                           K1=SI(0.7e6,  "J/m^3"),
                           K2=SI(0.18e6, "J/m^3"))
anisotropy.declare("SpaceField", "K1")

mat_Co = nmag.MagMaterial(
            name="Co",
            Ms=SI(1.42444e6, "A/m"),
            exchange_coupling=SI(3.02e-11, "J/m"),
            anisotropy=anisotropy,
            llg_gamma_G=SI(0.2211e6, "m/ A s"),
            llg_normalisationfactor=SI(0.001e12, "1/s"))

mesh_name = "uniaxial_1d"
mesh_unit = SI(1e-9, "m")
new_mesh = True

#--------------------------------------------
## The initial configuration and how the applied field should change

m0 = [1, 0, 1] # Initial direction for the magnetisation

# From the norms and the direction (which is constant) we derive
# all the values that the applied field will take during the simulation
Hs = vector_set(direction=[1, -2, 3],
                norm_list=[-3.0, [200], 3.0],
                units=SI(1e6, "A/m"))

#--------------------------------------------
## Here we set up the simulation

# Create the simulation object
sim = nmag.Simulation("uniaxial_1d", do_demag=True)

# Creates the mesh from the layer structure
sim.load_mesh("bar.nmesh.h5", [("Co", mat_Co)], unit_length=SI(1e-9, "m"))

sim.model.write_dependency_tree()
#raw_input()


sim.set_m(m0) # Set the initial magnetisation

# Set additional parameters for the time-integration
#sim.set_timestepper_params(stopping_dm_dt=1*degrees_per_ns)
sim.set_params(ts_abs_tol=1e-6, ts_rel_tol=1e-6)

#--------------------------------------------
## Run the simulation to calculate the hysteresis loop

from nsim.when import every, at
sim.hysteresis(Hs,
               save=[('averages', at('convergence'))],
               convergence_check=every(5, 'step'))

