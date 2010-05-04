from nsim.si_units.si import SI
from nsim.model import *
import nmesh
from nmag import MagMaterial

# Units
ps = SI(1e-12, "s") # Picosecond

# Constants
negJ = Constant("negJ", def_on_material=True)
M_sat = Constant("M_sat", def_on_material=True)
gamma_LL = Constant("gamma_LL", def_on_material=True)
alpha = Constant("alpha", def_on_material=True)

# All fields
m = SpaceField("m", [3], def_on_material=True)
H_ext = SpaceField("H_ext", [3])
E_total = SpaceField("E_total", [], def_on_material=True)
rho = SpaceField("rho", [])
dmdt = SpaceField("dmdt", [3], def_on_material=True)
M = SpaceField("M", [3], def_on_material=True)
H_exch = SpaceField("H_exch", [3], def_on_material=True)
H_anis = SpaceField("H_anis", [3], def_on_material=True)
H_total = SpaceField("H_total", [3], def_on_material=True)
E_demag = SpaceField("E_demag", [], def_on_material=True)
E_ext = SpaceField("E_ext", [], def_on_material=True)
E_anis = SpaceField("E_anis", [], def_on_material=True)

# Set the values of the constants and initial values of the fields
gamma_LL.set_value(1.0, 'Py')
alpha.set_value(0.5, 'Py')

# Computation of exchange field
tree = OverMatNode(
       MulNode(QuantityNode(negJ),
               UnparsedNode("<d/dxj ${H_exch(k)}||d/dxj ${m(k)}>")))
op_H_exch = OperatorContext(tree.simplify(),
                            inputs=[negJ, m],
                            outputs=[H_exch])

# Computation of divergence of M
tree = \
  OverMatNode(
    SumNode(MulNode(QuantityNode(M_sat),
                    UnparsedNode("<${rho}||d/dxj ${m(j)}>")),
            MulNode(QuantityNode(M_sat),
                    UnparsedNode("<${rho}||D/Dxj ${m(j)}>"))))
op_div_m = OperatorContext(tree.simplify(),
                           inputs=[M_sat, rho],
                           outputs=[m])

# Definition of H_total
comp_H_total = Equation("H_total", "%range i:3; H_total(i) <- H_ext(i);")

# Equation of motion
comp_llg = Equation("comp_llg", """
%range i:3, j:3, k:3, p:3, q:3;
dmdt(i) <- (-gamma_LL) * eps(i,j,k)*m(j)*H_total(k) +
           (-gamma_LL*alpha) * eps(i,j,k)*m(j)*eps(k,p,q)*m(p)*H_total(q);""")

# Equation for the Jacobian
#jacobian_llg = Equation("jacobian_llg", """
#%range i:3, j:3, k:3, p:3, q:3;
#dmdt(i) <- (-gamma_LL) * eps(i,j,k)*m(j)*H_total(k) +
           #(-gamma_LL*alpha) * eps(i,j,k)*m(j)*eps(k,p,q)*m(p)*H_total(q);""")

ts = Timestepper("ts_llg", x='m', dxdt='dmdt', eq_for_jacobian=comp_llg,
                 time_unit=ps)

# All materials
mat_Py = MagMaterial('Py')

# Load mesh
mesh = nmesh.load("mesh.nmesh.h5")
region_materials = [[], [mat_Py]]

# Put everything together in a physical model
p = Model("mumag", mesh, region_materials)
p.add_quantity([alpha, gamma_LL,
                m, H_ext, E_total, dmdt, M, H_exch, H_anis, H_total,
                E_demag, E_ext, E_anis])
p.add_computation([comp_llg, comp_H_total])
p.add_timestepper(ts)

p.build()

ts.advance_time(100*ps)
