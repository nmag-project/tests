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


time_ = dt*60
print "Simulated time: %s" % time_

t.start("advance-time")
target_time = sim.advance_time(time_)
t.stop("advance-time")

row_desc = ""
row_data = ""

timings = sim.get_timers()
for col in ["initialisation", "advance-time"]:
    state_str, time_reached, num_stops = t.get_state(col)
    assert state_str == "stopped", "Error while using the Timer"
    timings.append((col, num_stops, time_reached))

for col, num_stops, time_reached in timings:
    row_data += " %20.2f %4s" % (time_reached, num_stops)
    row_desc += " %20s %4s" % (col, "num.")

row_desc += " %20s" % "num. steps"
row_data += " %20d" % sim.step

file_existed = os.path.exists(outfile)
f = open(outfile, "a")
if not file_existed:
    f.write(row_desc + "\n")
f.write(row_data + "\n")
f.close()

# Save final magnetisation average and field so that we can check for
# correctness and we can extract the reordered mesh to check how it
# was partitioned
sim.save_data(fields='all')

