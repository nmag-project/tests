import time
import nmag
from nmag import SI,mesh
import os

execfile("../msat.inc")

time_total = -time.time()
time_writing = 0.0
time_initialising = -time.time()
mat_Py = nmag.MagMaterial(name="Py",
                          Ms=SI(M_SAT,"A/m"),
                          exchange_coupling=SI(13.0e-12, "J/m"),
                          llg_gamma_G=SI(0.2211e6, "m/A s"),
                          # llg_damping=SI(0,"")
                          )


sim = nmag.Simulation()

meshfile = "../bar30_30_100.nmesh.h5"

sim.load_mesh(meshfile, [("Py", mat_Py)],unit_length=SI(1e-9,"m"))

import math
angle_deg = 45
angle_rad = angle_deg/360.*2*math.pi
sim.set_m([math.cos(angle_rad), 0, math.sin(angle_rad)])

dt = SI(5e-12, "s") 

time_initialising += time.time()
time_loop = -time.time()

if False:
    for i in range(0, 61):
        time_ = dt*i
        print "Time spent so far %g" % (time_total+time.time())
        target_time = sim.advance_time(time_)

        time_writing -= time.time()
        if i % 10 == 0:
            sim.save_data(fields='all')
        else:
            sim.save_data()
    time_writing += time.time()

target_time = sim.advance_time(dt*60)
time_loop += time.time()

sim.save_data()

time_total += time.time()
time_simulating = time_loop - time_writing
print "Setup took %g seconds" % time_initialising
print "Simulation loop took %g seconds" % time_loop
print "Writing data took: %g seconds" % time_writing
print "Timestepper took: %g seconds" % time_simulating
print "Total time: %g seconds" % time_total

