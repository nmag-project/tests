import nmag
from nmag import SI
import nsim.testtools
import numpy

ellipsoid_size = numpy.array((10.0e-9, 8.0e-9, 6.0e-9))

def is_inside_mesh(r):
  # r should be a numpy array
  return (sum((r/ellipsoid_size)**2) < 1.0)

def H_ext(r):
  x, y, z = r
  hx = (x + 2*y + 3*z)*1e9
  return [hx, 2*hx, 3*hx]

def simulate():
  mesh_file = nsim.testtools.get_test_mesh(size="small")
  sim = nmag.Simulation(do_demag=False)
  material = nmag.MagMaterial("a")
  sim.load_mesh(mesh_file, [("region", material)], unit_length=SI(1e-9, "m"))
  sim.set_m([1, 0, 0])
  sim.set_H_ext(H_ext, unit=SI("A/m"))
  sim.save_data(fields="all")

def check(filename):
  import numpy
  rows = numpy.loadtxt(filename)
  zeros = numpy.array([0]*3)
  error = 0.0
  for row in rows:
    pos = 1e-9 * row[1:4]
    val = row[4:7]
    expected_val = (H_ext(pos) if is_inside_mesh(pos) else zeros)
    error += sum((val - expected_val)**2)

  error /= len(rows)
  assert (error**0.5) < 1e-6
    

import sys
if "check" in sys.argv:
  check("real-space.dat")

else:
  simulate()

