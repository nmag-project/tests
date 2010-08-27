import os, sys
from nmag.common import *
from nmag import vector_set

mat_Py = MagMaterial(name='Py',
                     Ms=SI(0.86e6, 'A/m'),
                     llg_damping=0.2,
                     llg_gamma_G=SI(2.210173e5, "m/A s"),
                     exchange_coupling=SI(13.0e-12, 'J/m'))

s = Simulation()

s.load_mesh("mesh.nmesh.h5", [('Py', mat_Py)], unit_length=SI(1e-9, 'm'))

def m0(r):
    x, y, z = [xi*1e9 for xi in r]
    return [x, y + 10, z + 25.0]

s.set_m(m0)
s.set_H_ext([0, 0, 1e5], unit=SI("A/m"))
s.set_params(stopping_dm_dt=0.0*degrees_per_ns)
s.relax(do=[('exit', at('time', SI(1e-9, "s")))],
        save=[('averages', every('time', SI(10e-12, "s"))),
              ('fields', at('time', SI(0, "s")) | at('time', SI(1e-9, "s")))])

