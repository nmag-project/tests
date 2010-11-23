from nsim.model import *
import nmesh
from nmag import MagMaterial

# Constants and fields
#M_sat = Constant("M_sat", subfields=True, value=Value(0.86e6))

rho = Constant("rho", subfields=False, value=Value(8700))
C = Constant("C", subfields=False, value=Value(430))
sigma = Constant("sigma", subfields=False, value=Value(4e6))

#gamma_GG = Constant("gamma_GG", subfields=True, value=Value(2.210173e5))
#alpha = Constant("alpha", subfields=True, value=Value(0.2))
#m = SpaceField("m", [3], subfields=True, value=Value([1, 0, 0]))
#H_ext = SpaceField("H_ext", [3], value=Value([0, 0, 1.0e5]))
#dmdt = SpaceField("dmdt", [3], subfields=True)

j = SpaceField("j", [3], value=Value([1, 0, 0]))
T = SpaceField("T", [], subfields=False, value=Value(0))
dTdt = SpaceField("dTdt", [], subfields=False)



# Equation of motion
heatconduction = Equation("heatconduction", """
%range i:3;
dTdt <- j(i)*j(i)/(rho*C*sigma)+(4-T);""")

# Timestepper
ts = Timestepper("ts_heatconduction", x='T', dxdt='dTdt', eq_for_jacobian=heatconduction)

# Put everything together in a physical model
mesh = nmesh.load("mesh.nmesh.h5")
region_materials = [[], ["Py"]]
p = Model("mumag", mesh, 1e-9, region_materials)


p = Model("heat", mesh, 1e-9, region_materials)

p.add_quantity([rho,C,sigma,j,T,dTdt])
p.add_computation(heatconduction)
p.add_timestepper(ts)
p.build()

# Now we can use the model
f = open("model.dat", "w")
f.write("%g " % 0 + "%g\n" % T.compute_average().as_float())
for i in range(1, 101):
  t = i*10e-12
  ts.advance_time(t)
  f.write("%g " % t + "%g\n" % T.compute_average().as_float())
f.close()
