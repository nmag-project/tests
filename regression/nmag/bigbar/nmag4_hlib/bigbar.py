import time,sys
import nmag
from nmag import SI,mesh
import os

ocaml.init_hlib("/home/aknittel/HLib-1.3/Library/.libs/libhmatrix-1.3.so")
execfile("../msat.inc")


parameters={"ACA":[0,3,30,2.0,0.0001,0.001,5,100],"ACA+":[1,3,30,2.0,0.0001,0.001,5,100],"Interpolation":[2,3,30,2.0,0.0001,0.001,5,100],"HCAI":[3,3,30,2.0,0.0000001,0.001,6,100],"HCAII":[4,3,30,2.0,0.0000001,0.001,4,100]}

algorithmlist=[item for item in parameters.iterkeys()]
algorithm=sys.argv[1]
assert (algorithm in algorithmlist)

hp = {}
hp['algorithm']=parameters[algorithm][0]
hp['nfdeg'] = parameters[algorithm][1]
hp['nmin'] = parameters[algorithm][2]
hp['eta'] = parameters[algorithm][3]
hp['eps_aca'] = parameters[algorithm][4]
hp['eps'] = parameters[algorithm][5]
hp['p'] = parameters[algorithm][6]
hp['kmax'] = parameters[algorithm][7]

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


sim = nmag.Simulation(use_hlib=True, hlib_params=hp)

meshfile = "../bar30_30_100.nmesh.h5"

sim.load_mesh(meshfile, [("Py", mat_Py)],unit_length=SI(1e-9,"m"))

import math
angle_deg = 45
angle_rad = angle_deg/360.*2*math.pi
sim.set_m([math.cos(angle_rad), 0, math.sin(angle_rad)])
sim.set_params(ts_rel_tol=2.7e-05 , ts_abs_tol=2.7e-05)

dt = SI(5e-12, "s") 

time_initialising += time.time()
time_loop = -time.time()
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

time_loop += time.time()


time_total += time.time()
time_simulating = time_loop - time_writing
print "Setup took %g seconds" % time_initialising
print "Simulation loop took %g seconds" % time_loop
print "Writing data took: %g seconds" % time_writing
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
rev = "$Revision$"[11:-2] #This file's version
import nsim
import nsim.svnversion
rev = nsim.svnversion.svnversion #global version -> more useful
out("# Timings for the bigbar unit test\n" \
    "# host\t Rev\t date sim\t init\t writing-data\t sim&writing-data\t total\tRev\n", header=True)
out("%s \t%s \t%s \t%g \t%g \t%g \t%g \t%g\n" % (host, rev, date,time_simulating, time_initialising, time_writing, time_loop, time_total))

print "=== LAM Timings ===\n",sim.get_timers()

#print "=== CVODE Timings ===\n",sim.timestepper.get_stats() still not available for parallel timestepper

