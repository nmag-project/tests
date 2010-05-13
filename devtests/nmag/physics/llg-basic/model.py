from nsim.model import *
import nmesh
from nmag import MagMaterial

# Constants and fields
M_sat = Constant("M_sat", subfields=True, value=Value(0.86e6))
gamma_GG = Constant("gamma_GG", subfields=True, value=Value(2.210173e5))
alpha = Constant("alpha", subfields=True, value=Value(0.2))
m = SpaceField("m", [3], subfields=True, value=Value([1, 0, 0]))
H_ext = SpaceField("H_ext", [3], value=Value([0, 0, 1.0e5]))
dmdt = SpaceField("dmdt", [3], subfields=True)

# Equation of motion
llg = Equation("llg", """
%range i:3, j:3, k:3, p:3, q:3;
dmdt(i) <- (-gamma_GG/(1 + alpha*alpha))*(eps(i,j,k)*m(j)*H_ext(k) +
           alpha*eps(i,j,k)*m(j)*eps(k,p,q)*m(p)*H_ext(q));""")

# Timestepper
ts = Timestepper("ts_llg", x='m', dxdt='dmdt', eq_for_jacobian=llg)

# All materials
mat_Py = MagMaterial('Py')

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
  t = i*10e-12
  ts.advance_time(t)
  f.write("%g " % t + "%g %g %g\n" % tuple(m.compute_average()[0][1]))
f.close()
