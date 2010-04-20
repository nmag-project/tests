from nsim.model import *
import nmesh
from nmag import MagMaterial

# Constants
damping_const = Constant("alpha", def_on_material=True)
negJ = Constant("negJ", def_on_material=True)
M_sat = Constant("M_sat", def_on_material=True)

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

# All materials
mat_Py = MagMaterial('Py')

# Load mesh
mesh = nmesh.load("mesh.nmesh.h5")
region_materials = [[], [mat_Py]]

# Put everything together in a physical model
p = Model("mumag", mesh, region_materials)
p.add_quantity([damping_const,
                m, H_ext, E_total, dmdt, M, H_exch, H_anis, H_total,
                E_demag, E_ext, E_anis])
p.add_computation([op_H_exch, op_div_m])
p.build()

