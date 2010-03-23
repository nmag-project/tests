#This is a very bizzare problem. If we run this file with
#
#$> pytest_nsim --testonlythisfile test_slow_demag_twomat2.py
#
#then all is well and we pass the test.
#
#If, instead, we run just
#
#$> pytest_nsim
#
#in this directory, then we get the odd error message (see ticket:176)
#
#I'll rename this test for the release (so that 'make checkall' will not
#fail). HF 20 Nov 2008


import sys, os
#setup_directories(
org_dir = os.getcwd()
debug=False
try:
  this_dir = os.path.split(__file__)[0]
except NameError:
  this_dir = os.getcwd()
  debug=True
out_file = os.path.join(this_dir,"test_slow_demag_twomat.dat")

def out(msg):
  f = open(out_file, "at")
  f.write(msg + "\n")
  f.close()

def do_simulation():

  import time
  import nmag

  #import nsim.logtools
  #import logging
  #
  #nsim.logtools.setGlobalLogLevel(logging.DEBUG)
  
  from nmag import SI, mesh
  import os

  mat1 = nmag.MagMaterial(name="mat1",
                          Ms=SI(0.8e6, "A/m"),
                          exchange_coupling=SI(13.0e-12, "J/m"),
                          llg_gamma_G=SI(0.2211e6, "m/A s"),
                          llg_damping=0.5)

  mat2 = nmag.MagMaterial(name="mat2",
                          Ms=SI(0.8e6, "A/m"),
                          exchange_coupling=SI(13.0e-12, "J/m"),
                          llg_gamma_G=SI(0.2211e6, "m/A s"),
                          llg_damping=0.5)

  sim1 = nmag.Simulation(name="simulation1")
  sim1.load_mesh("bar.nmesh.h5", 
                [("one", mat1), ("two", mat2)],
                unit_length=SI(1e-9,"m"))

  sim2 = nmag.Simulation(name="simulation2")
  sim2.load_mesh("bar.nmesh.h5",
                [("one", mat1), ("two", mat1)],
                unit_length=SI(1e-9,"m"))

  import math
  angle_deg = 45
  angle_rad = angle_deg/360.*2*math.pi

  sim2.set_m([math.cos(angle_rad), 0, math.sin(angle_rad)])
  sim2.set_params(ts_rel_tol=2.7e-05 , ts_abs_tol=2.7e-05)

  def norm(p):
    return math.sqrt(p[0]**2 + p[1]**2 + p[2]**2)

  def dist(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)

  # First we check consistency between the meshes
  ps1 = sim1.mesh.points
  ps2 = sim2.mesh.points
  if len(ps1) != len(ps2): raise "Mesh size inconsistency!"
  for i in range(len(ps1)):
    p1, p2 = (ps1[i], ps2[i])
    d = dist(p1, p2)
    if d > 1e-12:
      raise "Mesh coords inconsistency!"

  def build_key(p):
    return ",".join(["%8f" % round(pi, 6) for pi in p])

  # Now we can assume that the indexing is the same
  i = 0
  pcs = {}
  for p in ps1:
    pcs[build_key(p)] = i
    i += 1

  max_ds = []
  max_drels = []

  def consistency_check(_):
    m2 = sim2.get_subfield("m_mat1")

    def m(p):
      return m2[pcs[build_key([pi*1e9 for pi in p])]]

    sim1.set_m(m, "m_mat1")
    sim1.set_m(m, "m_mat2")

    Hd1 = sim1.get_subfield("H_demag")
    Hd2 = sim2.get_subfield("H_demag")
    if len(Hd1) != len(Hd2):
      raise "Demag field size mismatch!"
    n = len(Hd1)
    max_d = None
    max_drel = None
    for i in range(n):
      d = dist(Hd1[i], Hd2[i])
      if max_d == None or d > max_d:
        max_d = d
        max_drel = d/(norm(Hd1[i]) + norm(Hd2[i]))

    max_ds.append(max_d)
    max_drels.append(max_drel)

    msg = "Deviation in the demag fields: " \
          "absolute %s, percentual %s" % (max_d, max_drel)

    out(msg)

  from nmag import every
  sim2.relax(do=[(consistency_check, every("time", SI(50e-12, "s")))], save=[])

  assert max(max_drels) < 0.0011, "Test failed: demag differs by more than 0.1 %"
  assert max(max_ds) < 1000.0, "Test failed: demag differs by more than 1000 A/m"

def test_demag():
  os.chdir(this_dir)
  out(os.getcwd())
  os.system("make init >make.out 2>&1")
  do_simulation()
  os.chdir(org_dir)

if debug:
  test_demag()
