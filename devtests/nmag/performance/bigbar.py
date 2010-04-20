import nmag
from nmag import SI, mesh
import nsim.timings

import os, sys

t = nsim.timings.Timer('bigbar')

meshfile = sys.argv[1]
outfile = sys.argv[2]

t.start("initialisation")
mat_Py = nmag.MagMaterial(name="Py",
                          Ms=SI(0.86e6, "A/m"),
                          exchange_coupling=SI(13.0e-12, "J/m"),
                          llg_gamma_G=SI(0.2211e6, "m/A s"),
                          # llg_damping=SI(0,"")
                          )

sim = nmag.Simulation()

sim.load_mesh(meshfile, [("Py", mat_Py)], unit_length=SI(1e-9,"m"))

import math
angle_deg = 45
angle_rad = angle_deg/360.*2*math.pi
sim.set_m([math.cos(angle_rad), 0, math.sin(angle_rad)])
sim.set_params(ts_rel_tol=2.7e-05 , ts_abs_tol=2.7e-05)

ps = SI(1e-12, "s")
dt = 5*ps 

sim.advance_time(0*ps)
t.stop("initialisation")

t.start("total-simloop")
for i in range(0, 61):
    time_ = dt*i
    print "Simulated time: %s" % time_

    t.start("advance-time")
    target_time = sim.advance_time(time_)
    t.stop("advance-time")

    if i % 10 == 0:
        t.start("writing-field-data")
        sim.save_data(fields='all')
        t.stop("writing-field-data")
    else:
        t.start("writing-avg-data")
        sim.save_data()
        t.stop("writing-avg-data")
t.stop("total-simloop")

row_desc = ""
row_data = ""
for col in ["initialisation", "total-simloop", "advance-time",
            "writing-avg-data", "writing-field-data"]:
    state_str, time_reached, num_stops = t.get_state(col)
    assert state_str == "stopped", "Error while using the Timer"
    row_data += " %20.2f %4d" % (time_reached, num_stops)
    row_desc += " %20s %4s" % (col, "num.")

row_desc += " %20s" % "num. steps"
row_data += " %20d" % sim.step

file_existed = os.path.exists(outfile)
f = open(outfile, "a")
if not file_existed:
    f.write(row_desc + "\n")
f.write(row_data + "\n")
f.close()


