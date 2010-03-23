import time
import nmag
from nmag import SI,mesh,si,at,every
import os

execfile("../bigbar/msat.inc")

#import ocaml
#print "DDD SPEEDTEST: ",ocaml.ddd_speedtest_lindholm(939*939*2)

time_total = -time.time()
time_writing = 0.0
time_initialising = -time.time()
mat_Py = nmag.MagMaterial(name="Py",
                          Ms=SI(M_SAT,"A/m"),
                          exchange_coupling=SI(13.0e-12, "J/m"),
                          llg_gamma_G=SI(0.2211e6, "m/A s"),
                          # llg_damping=SI(0,"")
                          )


sim = nmag.Simulation(adjust_tolerances=True)

meshfile = "../bigbar/bar30_30_100.nmesh.h5"

sim.load_mesh(meshfile, [("Py", mat_Py)],unit_length=SI(1e-9,"m"))

import math
angle_deg = 45
angle_rad = angle_deg/360.*2*math.pi
sim.set_m([math.cos(angle_rad), 0, math.sin(angle_rad)])
sim.set_params(ts_rel_tol=1e-06 , ts_abs_tol=1.0e-06,stopping_dm_dt = 10*si.degrees_per_ns)

ps = SI(1e-12, "s") 


time_initialising += time.time()
time_loop = -time.time()

sim.relax(save = [('averages', every('time', 25*ps)|at('convergence')),
                  ('fields',at('convergence'))])

time_loop += time.time()

time_simulating = time_loop - nmag.timing['save_data']
print "Setup took %g seconds" % time_initialising
print "Simulation loop took %g seconds" % time_loop
print "Writing data took: %g seconds" % nmag.timing['save_data']
print "Timestepper took: %g seconds" % time_simulating
print "Total time: %g seconds" % time_total

def out(line, header=False, file="bigbar_timings.log"):
    import os
    if header and os.path.exists(file): return
    f = open(file, "a")
    f.write(line)
    f.close()

import commands
host = commands.getoutput("uname -n")
date = time.asctime()
rev = "$Revision: 4912 $"[11:-2] #This file's version
import nsim
import nsim.svnversion
rev = nsim.svnversion.svnversion #global version -> more useful
out("# Timings for the bigbar unit test\n" \
    "# host\t Rev\t date sim\t init\t writing-data\t sim&writing-data\t total\tRev\n", header=True)
out("%s \t%s \t%s \t%g \t%g \t%g \t%g \t%g\n" % (host, rev, date,time_simulating, time_initialising, nmag.timing['save_data'], time_loop, time_total))



#relax only start from 1e-6 -> 110 seconds, 1005 steps
#relax only start from 2.7e-5 -> 105 seconds, 900 steps
#dm_dt = 10 degree per ns -> 578 steps


