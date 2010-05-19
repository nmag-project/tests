from nmag.common import *

mat_Py = MagMaterial(name="Py",
                     Ms=SI(0.86e6, "A/m"),
                     exchange_coupling=SI(13.0e-12, "J/m"),
                     llg_gamma_G=SI(0.2211e6, "m/A s"))

sim = Simulation()

meshfile = "bar.nmesh.h5"

sim.load_mesh(meshfile, [("Py", mat_Py)],unit_length=SI(1e-9,"m"))

import math
angle_deg = 45
angle_rad = angle_deg/360.*2*math.pi
sim.set_m([math.cos(angle_rad), 0, math.sin(angle_rad)])
sim.set_params(ts_rel_tol=2.7e-05 , ts_abs_tol=2.7e-05)

dt = SI(5e-12, "s") 

for i in range(0, 1):
    target_time = sim.advance_time(i*dt)
    if i % 10 == 0:
        sim.save_data(fields='all')
    else:
        sim.save_data()

import nmag
nmag.ipython()

