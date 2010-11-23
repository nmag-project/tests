from nsim.model import *
import nmesh
from nmag import MagMaterial

# Constants and fields
rho = Constant("rho", subfields=False, value=Value(8700.0))
C = Constant("C", subfields=False, value=Value(430.0))
sigma = Constant("sigma", subfields=False, value=Value(4.0e6))

T = SpaceField("T", [], subfields=True, value=Value(1))
j = SpaceField("j", [3], value=Value([0, 0, 1.0e11]))
dTdt = SpaceField("dTdt", [], subfields=True)

# Equation of motion
llg = Equation("llg", """
%range i:3;
dTdt <- j(i)*j(i)/(rho*C*sigma);""")

# Timestepper
ts = Timestepper("ts_llg", x='T', dxdt='dTdt', eq_for_jacobian=llg)

# Put everything together in a physical model
mesh = nmesh.load("mesh.nmesh.h5")
region_materials = [[], ["Py"]]
p = Model("mumag", mesh, 1e-9, region_materials)
p.add_quantity([T, j, rho, C, sigma, dTdt])
p.add_computation(llg)
p.add_timestepper(ts)
p.build()

# Now we can use the model
f = open("model.dat", "w")
t = 0.0
for i in range(1, 101):
  f.write("%g %g\n" % (t, T.compute_average().as_float()))
  t += 10e-12
  ts.advance_time(t)

f.close()

