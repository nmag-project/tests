import os
import sys
import math

from nmag.constants import mu0, Tesla
from nsim.netgen import netgen_mesh_from_string

from nsim.si_units.si import SI, degrees_per_ns
from nmag.nmag5 import Simulation, MagMaterial, uniaxial_anisotropy
from nmag import at, every
from nsim.model import Value


theta = 40.0
phi = 90.0

scale = 0.1
nm = SI(1e-9, "m")
length = scale*125*nm
width  = scale*125*nm
thick  = 5*nm

do_sl_stt = True
I = scale**2 * SI(5e-3, "A")
current_density = I/(length*width)

Happ_norm = 0.001*Tesla/mu0
Happ_dir = [0.2, 0.2, 10.0]

ps = SI(1e-12, "s")

mesh_filename = "film.nmesh.h5"
if not os.path.exists(mesh_filename):
  mesh_geo = \
    ("algebraic3d\n"
     "solid cube = orthobrick (0, 0, 0; %s, %s, %s) -maxh = 2.5;\n"
     "tlo cube;\n" % tuple(map(lambda x: float(x/nm), (length, width, thick))))

  netgen_mesh_from_string(mesh_geo, mesh_filename, keep_geo=True)


anis = uniaxial_anisotropy(axis=[0, 0, 1], K1=-SI(0.1e6, "J/m^3"))
mat = MagMaterial("Py",
                  Ms=SI(860e3, "A/m"),
                  exchange_coupling=SI(13e-12, "J/m"),
                  llg_gamma_G=SI(221017, "m/s A"),
                  llg_damping=SI(0.014),
                  anisotropy=anis)

if do_sl_stt:
  mat.sl_P = 0.4             # Polarisation
  mat.sl_d = SI(5.0e-9, "m") # Free layer thickness

sim = Simulation(do_sl_stt=do_sl_stt, do_demag=False)
sim.load_mesh(mesh_filename, [("region1", mat)], unit_length=nm)

sim.set_m([1, 0.01, 0.01])
sim.set_H_ext(Happ_dir, Happ_norm)

if do_sl_stt:
  # Direction of the polarization
  theta_rad = math.pi*theta/180.0
  phi_rad = math.pi*phi/180.0
  P_direction = [math.sin(theta_rad)*math.cos(phi_rad),
                 math.sin(theta_rad)*math.sin(phi_rad),
                 math.cos(theta_rad)]

  sim.model.quantities["sl_fix"].set_value(Value(P_direction))

  # Current density
  sim.model.quantities["sl_current_density"].set_value(Value(current_density))

sim.set_params(stopping_dm_dt=0*degrees_per_ns,
               ts_rel_tol=1e-7, ts_abs_tol=1e-7)
sim.relax(save=[("averages", every("time", 5*ps))],
          do=[("exit", at("time", 10000*ps))])

#ipython()

