from nmag.common import *
import nmag
import math

mat_Py = MagMaterial('Py',
                     Ms=SI(0.86e6, 'A/m'),
                     exchange_coupling=SI(13.0e-12, 'J/m'),
                     llg_polarisation=1.0,
                     llg_xi=0.01,
                     llg_damping=0.01)

s = Simulation(phi_BEM=nmag.default_hmatrix_setup, do_demag=True)

s.load_mesh('nanowire.nmesh.h5',
            [('nanowire', mat_Py)],
            unit_length=SI(1e-9, 'm'))

def m0(r):
    x, y, z = [ri*1e9 for ri in r] # in nm
    angle = 0.5*math.pi*max(-1.0, min(1.0, (x - 500.0)/100.0))
    return [math.sin(angle), math.cos(angle), 0.0]

import os
file_name = "m0.h5"
if not os.path.exists(file_name):
  s.set_m(m0)
  s.relax(save=[('fields', at('time', SI(0, 's')) | at('convergence'))])
  s.save_restart_file(file_name)
  import sys
  sys.exit(0)

s.load_m_from_h5file(file_name)
s.set_current_density([1.0e12, 0, 0], unit=SI("A/m^2"))
s.relax(save=[('fields', every('time', SI(10e-12, 's')))],
        do=[('exit', at('time', SI(2e-9, 's')))])

