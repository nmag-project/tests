# RUN WITH: mpirun -np 2 `pwd`/../../../bin/nsim run.py --clean
import time, os, sys, math
import nmag
from nmag import SI, mesh, every, at

distrib = None
use_pvode = False
if ocaml.petsc_is_mpi():
    nr_cpus = ocaml.petsc_mpi_nr_nodes()
    print "RUNNING WITH MPI!\nNR. CPUs: ", nr_cpus
    sys.stdout.flush()
    nr_points = 2117
    use_pvode = True
    points_per_cpu = int(nr_points/nr_cpus)
    distrib = [points_per_cpu for _ in range(nr_cpus-1)]
    #distrib.append(nr_points - sum(distrib)) # This doesn't work! Why???
    distrib = [nr_points - sum(distrib)] + distrib
    print distrib, sum(distrib)
    raw_input()


time_total = -time.time()
time_writing = 0.0
time_initialising = -time.time()

mat_Py = nmag.MagMaterial(name="Py",
                          Ms=SI(0.86e6, "A/m"),
                          exchange_coupling=SI(13.0e-12, "J/m"),
                          llg_gamma_G=SI(0.2211e6, "m/A s"),
                          llg_damping=SI(0.5))

sim = nmag.Simulation(use_pvode=use_pvode)

meshfile = "bar_ordered.nmesh.h5"

sim.load_mesh(meshfile,
              [("Py", mat_Py)],
              unit_length=SI(1e-9,"m"),
              distrib=distrib)

angle_deg = 45.0
angle_rad = angle_deg * math.pi/180.
sim.set_m([math.cos(angle_rad), 0, math.sin(angle_rad)])
#sim.set_params(ts_rel_tol=2.7e-05 , ts_abs_tol=2.7e-05) # still not available

dt = SI(5e-12, "s") 

# Fields for which we run the hysteresis loop
Hs = nmag.vector_set(direction=[0.001, 0.001, 1.0],
                     norm_list=[1.0, 0.9, [], 0.3, 0.28, [], -0.3, -0.4, -1.0],
                     units=SI(1e6, "A/m"))

Hs = nmag.vector_set(direction=[0.001, 0.001, 1.0],
                     norm_list=[1.0, 0.99, [], -1.0],
                     units=SI(1e6, "A/m"))

def clocked_save(sim):
    global time_writing
    time_writing -= time.time()
    sim.save_data(fields='all', avoid_same_step=True)
    sim.save_data(avoid_same_step=True)
    time_writing += time.time()

time_initialising += time.time()

time_loop = -time.time()
sim.hysteresis(Hs, save=[(clocked_save, at('convergence'))])
time_loop += time.time()

time_total += time.time()
time_simulating = time_loop - time_writing
print "Setup took %g seconds" % time_initialising
print "Simulation loop took %g seconds" % time_loop
print "Writing data took: %g seconds" % time_writing
print "Timestepper took: %g seconds" % time_simulating
print "Total time: %g seconds" % time_total
