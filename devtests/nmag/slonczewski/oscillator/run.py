import os
import sys
import math

from nsim.si_units.si import SI, degrees_per_ns
from nmag.nmag5 import Simulation, MagMaterial
from nmag import at, every
from nsim.model import Value

relaxed_m = "m0.h5"
film_centre = (5, 50, 50)

do_relaxation = not os.path.exists(relaxed_m)
ps = SI(1e-12, "s")

mat = MagMaterial("Py",
                  Ms=SI(0.86e6, "A/m"),
                  exchange_coupling=SI(13e-12, "J/m"),
                  llg_damping=SI(0.5 if do_relaxation else 0.01))

mat.sl_P = 0.0 if do_relaxation else 0.4
mat.sl_d = SI(3e-9, "m")

sim = Simulation()
sim.load_mesh("mesh.nmesh.h5", [("region1", mat)], unit_length=SI(1e-9, "m"))

def m0(r):
  dx, dy, dz = tuple(ri - ri0*1e-9 for ri, ri0 in zip(r, film_centre))
  v = (1.0e-9, dz, -dy)
  vn = (1.0e-9**2 + dy*dy + dz*dz)**0.5
  return tuple(vi/vn for vi in v)

sim.set_m(m0)

sim.set_H_ext([0, 0, 0], SI("A/m"))
sim.model.quantities["sl_fix"].set_value(Value([0, 1, 0]))
sim.model.quantities["sl_current_density"].set_value(Value(SI(0.1e12, "A/m^2")))

if do_relaxation:
  print "DOING RELAXATION"
  sim.relax(save=[("fields", at("time", 0*ps) | at("convergence"))])
  sim.save_m_to_file(relaxed_m)
  sys.exit(0)

else:
  print "DOING DYNAMICS"
  sim.load_m_from_h5file(relaxed_m)
  sim.set_params(stopping_dm_dt=0*degrees_per_ns)
  sim.relax(save=[("averages", every("time", 5*ps))],
            do=[("exit", at("time", 10000*ps))])

#ipython()

