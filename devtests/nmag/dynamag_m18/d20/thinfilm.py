# One dimensional magnetic system studied using nsim
import os, sys, math
import nmag
from nmag import SI, vector_set, every, at
from nsim.si_units.si import degrees_per_ns

ps = SI(1e-12, "s"); nm = SI(1e-9, "m")

mat_A = nmag.MagMaterial(name="A",
                         Ms=SI(0.5e6, "A/m"),
                         exchange_coupling=SI(13.0e-12, "J/m"),
                         llg_damping=0.5)

anis_B = nmag.uniaxial_anisotropy(axis=[1, 0, 0], K1=SI(0.1e6, "J/m^3"))
mat_B =  nmag.MagMaterial(name="B",
                          Ms=SI(0.5e6, "A/m"),
                          exchange_coupling=SI(10.0e-12, "J/m"),
                          anisotropy=anis_B,
                          llg_damping=0.1)

# Create the simulation object
sim = nmag.Simulation()

# Set the coupling between the two magnetisations
sim.set_local_magnetic_coupling(mat_A, mat_B, SI(-1.0e-5, "N/A^2"))

# Load the mesh
sim.load_mesh("thinfilm.nmesh.h5", [("mesh", [mat_A, mat_B])], unit_length=1*nm)

# Set additional parameters for the time-integration
sim.set_params(stopping_dm_dt=1*degrees_per_ns,
               ts_rel_tol=1e-6, ts_abs_tol=1e-6)

sim.set_m([1, 0, 0], 'm_A') # Set the initial magnetisation
sim.set_m([-1, 0, 0], 'm_B')

Hs = vector_set(direction=[0.01, 0.01, 1],
                norm_list=[1.0, 0.95, [], -1.0],
                units=SI(1e6, "A/m"))

sim.hysteresis(Hs, save=[('averages', at('convergence'))])
#sim.hysteresis(Hs, save=[('averages', every('time', 1e5*ps) | at('convergence'))])

