import nmag
from nmag import SI, at, every
from nsim.netgen import NetgenMesh
import os.path, math

ps = SI(1e-12, 's')
nm = SI(1e-9, 'm')

######

# Details about the mesh
mesh_filename = 'bar.nmesh.h5'
bar_length, bar_crossec1, bar_crossec2 = 400.0, 4.0, 4.0
discretisation = 2.0

# Details about the disturbance region (a sphere)
disturb_origin = [0.0, bar_crossec1*0.5, bar_crossec2*0.5]
disturb_radius = bar_crossec1
disturb_direction = [0, 1, 0]
disturb_amplitude = SI(1e5, 'A/m')
disturb_duration = 1*ps

# Name of the file which will contain the relaxed magnetisation
m0_filename = 'm0.h5'

######

relaxed = os.path.exists(m0_filename)
if not os.path.exists(mesh_filename):
  relaxed = False
  vars = {'bar_length': bar_length, 
          'bar_crossec1': bar_crossec1, 
          'bar_crossec2': bar_crossec2,
          'discretisation': discretisation}

  m = NetgenMesh()
  m.set_vars(vars)
  m.geo("""
algebraic3d
solid bar = orthobrick (0, 0, 0; $bar_length$, $bar_crossec1$, $bar_crossec2$)
            -maxh = $discretisation$;
tlo bar;
  """)
  m.save(mesh_filename)

permalloy = nmag.MagMaterial('Py',
                             Ms=SI(0.86e6, 'A/m'),
                             exchange_coupling=SI(13e-12, 'J/m'),
                             llg_damping=[0.5, 0.02][relaxed])


s = nmag.Simulation(['rlx', 'dyn'][relaxed])

s.load_mesh(mesh_filename, [('bar', permalloy)], unit_length=1*nm)

def set_disturbance(is_on):
  c = float(nm/SI('m'))
  def setter(sim):
    def H_ext(r):
      x, y, z = [xi/c - x0i 
                 for xi, x0i in zip(r, disturb_origin)]
                # x, y and z are (floats) in nanometers
      d = math.sqrt(x*x + y*y + z*z)
      if is_on and d < disturb_radius:
        return disturb_direction
      else:
        return [0.0, 0.0, 0.0]
    sim.set_H_ext(H_ext, unit=disturb_amplitude)

  return setter

if not relaxed:
  s.set_m([1, 0, 0])
  s.relax()
  s.save_restart_file(m0_filename)

else:
  s.load_m_from_h5file(m0_filename)
  s.relax(save=[('field_m', every('time', 0.5*ps))],
          do=[(set_disturbance(True), at('time', 0*ps)),
              (set_disturbance(False), at('time', disturb_duration)),
              ('exit', at('time', 1000*ps))])

