import nmag
from nmag import SI, at, every
from nsim.netgen import NetgenMesh
import os.path, math

nm = SI(1e-9, 'm')
ps = SI(1e-12, 's')

# Details about the disturbance region (a sphere)
disturb_origin = [-50.0, 0.0, 0.0]
disturb_thickness = 0.5
disturb_direction = [0, 1, 0]
disturb_amplitude = SI(1e5, 'A/m')
disturb_duration = 1*ps

m0_filename = "m0.h5"

def simulate_nanowire(name, damping):
  permalloy = nmag.MagMaterial('Py',
                               Ms=SI(0.86e6, 'A/m'),
                               exchange_coupling=SI(13e-12, 'J/m'),
                               llg_damping=damping)

  s = nmag.Simulation(name)
  s.load_mesh("cylinder.nmesh.h5", [('nanopillar', permalloy)],
              unit_length=nm)
  return s

s = simulate_nanowire('relaxation', 0.5)
s.set_m([1, 0, 0])
s.relax(save=[('fields', at('time', 0*ps) | at('convergence'))])
s.save_restart_file(m0_filename)
del s

def set_to_zero(sim):
  def H_ext(r):
    return [0.0, 0.0, 0.0]
  sim.set_H_ext(H_ext, unit=disturb_amplitude)

c = float(nm/SI('m'))
def set_disturbance(sim):
  def H_ext(r):
    x, y, z = [xi/c - x0i
               for xi, x0i in zip(r, disturb_origin)]
               # x, y and z are (floats) in nanometers
    d = math.sqrt(x*x + y*y + z*z)
    if x < disturb_thickness:
        return disturb_direction
    else:
        return [0.0, 0.0, 0.0]

  sim.set_H_ext(H_ext, unit=disturb_amplitude)

s = simulate_nanowire('dynamics', 0.05)
s.load_m_from_h5file(m0_filename)
s.relax(save=[('fields', every('time', 0.5*ps))],
        do=[(set_disturbance, at('time', 0*ps)),
            (set_to_zero, at('time', disturb_duration)),
            ('exit', at('time', 5000*ps))])

