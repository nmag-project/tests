from nsim.si_units.si import SI
from nsim.model import *
import nmesh
from nmag import MagMaterial

# Units
ps = SI(1e-12, "s") # Picosecond

# Constants and fields
M_sat = Constant("M_sat", def_on_material=True)
gamma_LL = Constant("gamma_LL", def_on_material=True)
alpha = Constant("alpha", def_on_material=True)
m = SpaceField("m", [3], def_on_material=True)
H_ext = SpaceField("H_ext", [3])
dmdt = SpaceField("dmdt", [3], def_on_material=True)
M = SpaceField("M", [3], def_on_material=True)

# Set the values of the constants and initial values of the primary fields
gamma_LL.set_value(1.0, 'Py')
alpha.set_value(0.5, 'Py')

# Equation of motion
llg = Equation("llg", """
%range i:3, j:3, k:3, p:3, q:3;
dmdt(i) <- (-gamma_LL) * eps(i,j,k)*m(j)*H_ext(k) +
           (-gamma_LL*alpha) * eps(i,j,k)*m(j)*eps(k,p,q)*m(p)*H_ext(q);""")

# Timestepper
ts = Timestepper("ts_llg", x='m', dxdt='dmdt', eq_for_jacobian=llg,
                 time_unit=ps)

# All materials
mat_Py = MagMaterial('Py')

# Load mesh
mesh = nmesh.load("mesh.nmesh.h5")
region_materials = [[], [mat_Py]]

# Put everything together in a physical model
p = Model("mumag", mesh, region_materials)
p.add_quantity([alpha, gamma_LL, m, H_ext, dmdt, M])
p.add_computation(llg)
p.add_timestepper(ts)
p.build()

# Now we can use the model
ts.advance_time(100*ps)
