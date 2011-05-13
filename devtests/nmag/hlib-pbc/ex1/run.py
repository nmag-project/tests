from nmag import SI, every, at
import nmag

nm = SI(1e-9, "m")
ps = SI(1e-12, "s")
ns = 1000*ps

def run_simulation(periodic=False, use_hlib=False):
  phi_BEM = (nmag.default_hmatrix_setup if use_hlib else None)
  if periodic:
    pts = [[i*(15.0 + 0.1), 0, 0] for i in (-3, -2, -1, 1, 2, 3)]
    pbc = nmag.SetLatticePoints(vectorlist=pts, scalefactor=nm)
    sim = nmag.Simulation("periodic", periodic_bc=pbc.structure,
                          phi_BEM=phi_BEM)

  else:
    sim = nmag.Simulation("full", phi_BEM=phi_BEM)

  mat = nmag.MagMaterial("Py",
                         Ms=SI(0.86e6, "A/m"),
                         exchange_coupling=SI(13e-12, "J/m"),
                         llg_damping=0.5)

  mesh_file = "periodic.nmesh.h5" if periodic else "full.nmesh.h5"
  sim.load_mesh(mesh_file, [("mesh", mat)], unit_length=nm)

  sim.set_m([1, 1, 1])

  sim.relax(do=[("exit", at("time", 0.5*ns))],
            save=[("averages", every("time", 10*ps))])

import sys

run_simulation(periodic=("periodic" in sys.argv),
               use_hlib=("hlib" in sys.argv))

