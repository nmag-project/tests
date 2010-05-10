import os, sys
from nmag.common import *
from nmag import vector_set

mat_Py = MagMaterial(name='Py',
                     Ms=SI(0.86e6, 'A/m'),
                     llg_damping=0.2,
                     llg_gamma_G=SI(2.210173e5, "m/A s"),
                     exchange_coupling=SI(0.0e-12, 'J/m'))

s = Simulation(do_demag=False)

s.load_mesh("mesh.nmesh.h5", [('Py', mat_Py)], unit_length=SI(1e-9, 'm'))

s.set_m([1, 0, 0])
s.set_H_ext([0, 0, 1e5], unit=SI("A/m"))
s.set_params(stopping_dm_dt=0.0*degrees_per_ns)
s.relax(save=[('averages', every('time', SI(10e-12, "s")))],
        do=[('exit', at('time', SI(1e-9, "s")))])
