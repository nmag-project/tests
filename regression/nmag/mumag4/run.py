import nmag
from nmag import SI, hlib, every, at
from nsim.si_units.si import Tesla, mu0
import sys, os.path

mT = Tesla*0.001

def new_simulation(name, alpha=0.02):
  hlib_path = "/home/aknittel/HLib-1.3/Library/.libs/libhmatrix-1.3.so"
  ocaml.init_hlib(hlib_path)
  hmatrix = hlib.HLib()

  m_Py = nmag.MagMaterial(name="Py",
                          Ms=SI(8.0e5, "A/m"),
                          exchange_coupling=SI(1.3e-11, "J/m"),
                          llg_damping=alpha,
                          llg_gamma_G=SI(2.211e5, "m/A s"))

  s = nmag.Simulation(name, phi_BEM=hmatrix)
  s.load_mesh("sp4.nmesh.h5", [('bar', m_Py)], unit_length=SI(1e-9, 'm'))
  return s

# Obtain the initial magnetisation configuration (S-state) if necessary
m0_file = "m0.h5"
if "relax" in sys.argv:
  s = new_simulation('relaxation', alpha=1.0)
  Hs = nmag.vector_set(direction=[1, 1, 1],
                       norm_list=[1.00, 0.95, [], 0.0],
                       units=2e6*SI("A/m"))

  s.set_m([1, 1, 1])
  s.hysteresis(Hs)
  s.save_restart_file(m0_file)
  del s

# Run the dynamic simulation for field 1
if "field1" in sys.argv:
  s = new_simulation('field1')
  s.load_m_from_h5file(m0_file)
  s.set_H_ext([-24.6, 4.3, 0.0], mT/mu0)
  s.relax(save=[('averages', every('time', SI(10e-12, "s"))),
                ('fields', at('convergence'))])

# Run the dynamic simulation for field 2
if "field2" in sys.argv:
  s = new_simulation('field2')
  s.load_m_from_h5file(m0_file)
  s.set_H_ext([-35.5, -6.3, 0.0], mT/mu0)
  s.relax(save=[('averages', every('time', SI(10e-12, "s"))),
                ('fields', at('convergence'))])

