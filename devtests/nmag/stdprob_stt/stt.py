# Standard problem for spin-transfer torque (Zhang-Li model)
# We model a bar 200 nm x 200 nm x 20 nm where a vortex sits
# in the center. We study the reaction of the vortex to the
# application of an electric current.
#
import nmag
from nmag import SI, mesh
from nsim.when import every, at
from nsim.si_units.si import mu0, Tesla, degrees_per_ns
import os

restart_file = "relax_restart.h5"
if not os.path.exists(restart_file):
  llg_damping = 1.0
  llg_xi = 0.0
  j = 0 # A/m^2
  llg_polarisation = 0.0
  stopping_dm_dt = 1.0*degrees_per_ns
  sim_name = "relax"
  save = [('averages', every(1000, 'step') | at('convergence')),
          ('restart', at('stage_end'))]
  do = [('exit', at("time", SI(5e-9, "s")))]

else:
  llg_damping = 0.1
  llg_xi = 0.05
  j = 1e12 # A/m^2
  llg_polarisation = 1.0
  stopping_dm_dt=0.0
  sim_name = "stt"
  save = [('fields', at('convergence') | every('time', SI(1.0e-9, "s"))),
          ('averages', every('time', SI(0.1e-9, "s")) | at('stage_end'))]
  do = [('exit', at("time", SI(16e-9, "s")))]


mat_Py = nmag.MagMaterial(name="Py",
                          Ms=SI(0.8e6,"A/m"),
                          exchange_coupling=SI(13.0e-12, "J/m"),
                          llg_gamma_G=SI(0.2211e6, "m/A s"),
                          llg_polarisation=llg_polarisation,
                          llg_xi=llg_xi,
                          llg_damping=llg_damping,
                          llg_normalisationfactor=SI(0.1e12, "s^(-1)"))

sim = nmag.Simulation(sim_name, use_pvode=True)

meshfile = "stt.nmesh.h5"
sim.load_mesh(meshfile, [("Py", mat_Py)],unit_length=SI(1e-9,"m"))

c = [100.0e-9, 100.0e-9, 10.0e-9] # The center of the body
def m(p):
  v = [pi - ci for pi, ci in zip(p, c)]
  vo = [-v[1], v[0], 40.0e-9]
  # m will return a non normalized vector, nsim will normalize it anyway
  return vo

if j != 0.0:
  sim.load_m_from_h5file(restart_file)
  sim.set_current_density([j, 0, 0])
else:
  sim.set_m(m)

sim.set_params(ts_rel_tol=1e-06 ,
               ts_abs_tol=1e-06,
               stopping_dm_dt=stopping_dm_dt)

sim.relax(save=save, do=do)

