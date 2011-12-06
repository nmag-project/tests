import time
import nmag
from nmag import SI, mesh

mat1 = nmag.MagMaterial(name="mat1",
                        Ms=SI(0.8e6, "A/m"),
                        exchange_coupling=SI(13.0e-12, "J/m"),
                        llg_gamma_G=SI(0.2211e6, "m/A s"),
                        llg_damping=0.5)

sim1 = nmag.Simulation(name="simulation1")
sim1.load_mesh("bar.nmesh.h5", 
               [("one", mat1), ("two", mat1)],
               unit_length=SI(1e-9,"m"))

sim2 = nmag.Simulation(name="simulation2")
sim2.load_mesh("bar_oneregion.nmesh.h5",
               [("one", mat1)],
               unit_length=SI(1e-9,"m"))

import math
angle_deg = 45
angle_rad = angle_deg/360.*2*math.pi

# Setting first sim2.set_m, then sim1.set_m works. The other way
# throws an error (ticket:175)

print "Setting m for sim2"
sim2.set_m([math.cos(angle_rad), 0, math.sin(angle_rad)])
print "Setting m for sim1"
sim1.set_m([math.cos(angle_rad), 0, math.sin(angle_rad)])
print "Done (this is where ticket:175 would never get to)"

sim1.advance_time(SI(1e-15,'s'))
print "Done2"
sim2.advance_time(SI(1e-15,'s'))
print "Done3"

