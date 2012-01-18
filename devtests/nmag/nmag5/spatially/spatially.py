import os, sys, math

from nmag.constants import degrees_per_ns, mu0
from nmag.common import * # import every, at, etc.

# New Nmag5 imports: import nmag5 under the name "nmag"
from nmag.nmag5 import MagMaterial, Simulation, uniaxial_anisotropy, SI
from nsim.model import Value

anisotropy = \
  uniaxial_anisotropy(axis=[0, 0, 1], K1=SI(0.0, "J/m^3"))

mag = \
  MagMaterial(name="a",
              Ms=SI(0.5e6, "A/m"),
              exchange_coupling=SI(13e-12, "J/m"),
              anisotropy=anisotropy,
              llg_damping=0.5,
              llg_gamma_G=SI(0.2211e6, "m/A s"))

# Create the simulation object
sim = Simulation()

# We want some constants to be spatially dependent
sim.declare("spacefield", "alpha", "Ms", "gamma_G", "exchange_factor")
anisotropy.declare("spacefield", "K1")

# Load the mesh
mats = [("bottom", mag), ("top", mag)]
sim.load_mesh("spatially.nmesh.h5", mats, unit_length=SI(1e-9, "m"))

# Set additional parameters for the time-integration
sim.set_params(stopping_dm_dt=1*degrees_per_ns,
               ts_rel_tol=1e-6, ts_abs_tol=1e-6)

sim.set_m([0, 0, 1])
sim.set_H_ext([0, 0, 1], SI(100000, 'A/m'))

def create_setter(value_bottom, value_top, value_middle=None):
  # Fields in Nmag are defined on the nodes, which means that it is not
  # straightforward to decide how to set fields at the boundary. Here we
  # decide to set them as half of the values they have on each side.
  value_middle = \
    ([0.5*(v + value_top[i]) for i, v in enumerate(value_bottom)]
      if hasattr(value_middle, "__iter__")
      else 0.5*(value_top + value_bottom))

  def setter(position):
    x, y, z = position
    if z > 0.1e-9:
      r = value_top
    elif z < -0.1e-9 :
      r = value_bottom
    else:
      r = value_middle
    return r

  return setter

# Write on a file what Nmag5 did about the physics of the system
with open("model.desc", "w") as f:
   sim.model.write_debug_info(f)

# The values of the micromagnetic quantities on the layers.
# From left to right:
#  (1) the name of the parameter to set,
#  (2) the units of measurement to use for these last two numbers,
#  (3) the value of the parameter on the first layer,
#  (4) the value on the second layer.
vs = {"alpha": (      SI(1),    0.5,    0.5),   # damping
         "Ms": (  SI("A/m"), 0.69e6,  0.80e6),  # saturation mag.
          "A": (  SI("J/m"), 20e-12, 13.9e-12), # exchange coupling
         "K1": (SI("J/m^3"),    4e6,    0.0)}   # anisotropy constant

# We need to compute exchange_factor = 2*A/(mu0*Ms)
def exchange_factor(i):
    A = vs["A"][0] * vs["A"][1+i]
    Ms = vs["Ms"][0] * vs["Ms"][1+i]
    return -float((2.0*A/(mu0*Ms))/SI("A m"))
vs["exchange_factor"] = (SI("A m"), exchange_factor(0), exchange_factor(1))
vs.pop("A")

# Set the anisotropy constant K1
units, first, second = vs.pop("K1")
q = anisotropy.quantities["a0_K1"]
q.set_value(Value(create_setter(first, second), units))

# Set all the other quantities
for name, (units, first, second) in vs.iteritems():
  q = sim.model.quantities[name]
  q.set_value(Value(create_setter(first, second), units))

ps = SI(1e-12, "s")
sim.relax(save=[('fields', every('time', 10*ps))])
