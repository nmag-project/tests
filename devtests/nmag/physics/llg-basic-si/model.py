from nsim.model import *
import nmesh
from nmag import MagMaterial
from nsim.si_units import SI

# Constants and fields
M_sat = Constant("M_sat", subfields=True,
                 value=Value(0.86e6, SI("A/m")), unit=SI(1e6, "A/m"))
gamma_GG = Constant("gamma_GG", subfields=True,
                    value=Value(2.210173e5, SI("m/A s")), unit=SI(1e6, "m/A s"))
alpha = Constant("alpha", subfields=True, value=Value(0.2), unit=SI(1))
m = SpaceField("m", [3], subfields=True, value=Value([1, 0, 0]), unit=SI(1))
H_ext = SpaceField("H_ext", [3],
                   value=Value([0, 0, 1.0e5], SI("A/m")), unit=SI(1e6, "A/m"))
dmdt = SpaceField("dmdt", [3], subfields=True, unit=SI(1e12, "s"))

# Equation of motion
llg = Equation("llg", """
%range i:3, j:3, k:3, p:3, q:3;
dmdt(i) <- (-gamma_GG/(1 + alpha*alpha))*(eps(i,j,k)*m(j)*H_ext(k) +
           alpha*eps(i,j,k)*m(j)*eps(k,p,q)*m(p)*H_ext(q));""")

# Timestepper
ts = Timestepper("ts_llg", x='m', dxdt='dmdt', eq_for_jacobian=llg,
                 time_unit=SI(1e-12, "s"))

# Put everything together in a physical model
mesh = nmesh.load("mesh.nmesh.h5")
region_materials = [[], ["Py"]]
p = Model("mumag", mesh, region_materials)
p.add_quantity([alpha, gamma_GG, m, H_ext, dmdt])
p.add_computation(llg)
p.add_timestepper(ts)
p.build()

# Now we can use the model
f = open("model.dat", "w")
f.write("%g " % 0 + "%g %g %g\n" % tuple(m.compute_average()[0][1]))
for i in range(1, 101):
  t = i*SI(10e-12, "s")
  ts.advance_time(t)
  print m.compute_average()
  #f.write("%g " % t + "%g %g %g\n" % tuple(m.integrate()[0][1]))
f.close()
