# RUN WITH: mpirun -np 2 /home/you/nsim_path/bin/nsim hyst.py --clean

import time
import nmag
from nmag import SI, mesh
from nsim import sets
import os

class Timer:
  def __init__(self):
    self.timers = {}
  def start(self, timer_name):
    if self.timers.has_key(timer_name):
      self.timers[timer_name] -= time.time()
    else:
      self.timers[timer_name] = -time.time()
  def stop(self, timer_name):
    self.timers[timer_name] += time.time()
  def set(self, timer_name, timer_value):
    self.timers[timer_name] = timer_value
  def get(self, timer_name):
    return self.timers[timer_name]
  def show(self):
    for timer_name in self.timers:
      print "%s: %s" % (timer_name, self.timers[timer_name])

t = Timer()
t.start("total")
t.start("init")
mat_Py = nmag.MagMaterial(name="Py",
                          Ms=SI(0.8e6, "A/m"),
                          exchange_coupling=SI(13.0e-12, "J/m"),
                          llg_gamma_G=SI(0.2211e6, "m/A s"),
                          llg_damping=0.5)

sim = nmag.Simulation(use_pvode=True)

sim.load_mesh("bigbar.nmesh.h5",
              [("Py", mat_Py)],
              unit_length=SI(1e-9,"m"))

import math
angle_deg = 45
angle_rad = angle_deg/360.*2*math.pi
sim.set_m([math.cos(angle_rad), 0, math.sin(angle_rad)])
sim.set_params(ts_rel_tol=2.7e-05 , ts_abs_tol=2.7e-05)

# From the norms and the direction (which is constant) we derive
# all the values that the applied field will take during the simulation
Hs = sets.vector_set(direction=[1, -2, 3],
                     norm_list=[-1.0, [50], 1.0],
                     units=SI(1e6, "A/m"))

t.stop("init")
t.start("loop")

def save_averages(sim):
    t.start("write")
    sim.save_data(fields='all', avoid_same_step=True)
    t.stop("write")

from nsim.when import every, at
sim.hysteresis(Hs, save=[(save_averages, at("convergence"))])

t.stop("loop")
t.stop("total")
t.set("sim", t.get("loop") - t.get("write"))
t.show()

print "=== LAM Timings ===\n", sim.get_timers()

#print "=== CVODE Timings ===\n", sim.timestepper.get_stats()
