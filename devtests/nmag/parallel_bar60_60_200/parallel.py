import time, math,os,sys
import nmag
from nmag import SI,mesh


starttime = time.time()
def time_so_far(msg=None):
    time_spent = time.time()-starttime
    if msg:
        print "TIMING %s: %fs" % (msg,time_spent)
    return time_spent
    

# mpirun -np 2 /home/tf/ocaml/bin/nsim parallel.py

meshfile = "./bar60_60_200_ordered.nmesh.h5"

mat_Py = nmag.MagMaterial(name="Py",
                          Ms=SI(1e6,"A/m"),
                          exchange_coupling=SI(13.0e-12, "J/m"))

time_so_far( "Creating Simulation Object")
sim = nmag.Simulation()

time_so_far( "Loading mesh")
sim.load_mesh(meshfile, [("Py", mat_Py)],unit_length=SI(1e-9,"m"))
time_so_far( "Loaded mesh")

angle_deg = 45
angle_rad = angle_deg/360.*2*math.pi
time_so_far( "About to set m")
sim.set_m([math.cos(angle_rad), 0, math.sin(angle_rad)])

sim.set_params(ts_rel_tol=2.7e-05 , ts_abs_tol=2.7e-05)

#probed=sim.probe_subfield_siv('m_Py',[5e-9,5e-9,5e-9])
#print "### M at T=T0: ",probed

time_so_far("Calling advance time briefly (1e-18-) to setup Jacobian and all lazy things")
sim.advance_time(SI(1e-18,"s"))
time_so_far("Starting main loop")

tn = SI(50*10e-12,"s")
#tn = SI(1*10e-12,"s")

target_time = sim.advance_time(tn)

time_so_far("End main loop")

