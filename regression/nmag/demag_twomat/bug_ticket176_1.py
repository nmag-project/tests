"""This regression test computes the demag field for a given static
configuration of the magnetisation using two different meshes:

bar_oneregion:

|-----------------------|
|                       | 
|-----------------------|

bar:

|----------||-----------|
|          ||           | 
|----------||-----------|

Both regions in 'bar' are the same material, so that
expect roughly the same results.

HF Nov 2008
"""



import sys, os
#setup_directories
org_dir = os.getcwd()

debug = False
try:
  this_dir = os.path.split(__file__)[0]
except NameError: #thrown if not run through pytest_nsim (because __file__ is not defined)
  this_dir = os.getcwd()
  debug = True
  
out_file = os.path.join(this_dir,"test_demag_twomat1.dat")

def out(msg):
  f = open(out_file, "at")
  f.write(msg + "\n")
  f.close()

def do_simulation():
  import time
  import nmag
  from nmag import SI, mesh
  import os

  mat1 = nmag.MagMaterial(name="mat1",
                          Ms=SI(0.8e6, "A/m"),
                          exchange_coupling=SI(13.0e-12, "J/m"),
                          llg_gamma_G=SI(0.2211e6, "m/A s"),
                          llg_damping=0.5)

  sim1 = nmag.Simulation(name="simulation1")
  sim1.load_mesh("bar.nmesh.h5", 
                [("one", mat1), ("two", mat1)],
                unit_length=SI(1e-9,"m"))

  sim2 = nmag.Simulation(name="simulation2")
  sim2.load_mesh("bar_oneregion.nmesh.h5",
                [("one", mat1)],
                unit_length=SI(1e-9,"m"))

  import math
  angle_deg = 45
  angle_rad = angle_deg/360.*2*math.pi

  print "Setting m for sim1"
  sim1.set_m([math.cos(angle_rad), 0, math.sin(angle_rad)])
  print "Setting m for sim2"
  sim2.set_m([math.cos(angle_rad), 0, math.sin(angle_rad)])

  def consistency_check(m):
    import numpy
    sim1.set_m(m, "m_mat1")
    sim2.set_m(m, "m_mat1")

    Hd2 = sim1.get_subfield("H_demag")
    pos2 = sim1.get_subfield_positions("H_demag")

    assert len(Hd2) == len(pos2),"Internal error"


    Hd1 = numpy.zeros((len(Hd2),3),numpy.float64)

    print "Computing demag field via for-loop over probe (will take a while)"
    for i in range(len(pos2)):
      Hd1[i] = sim1.probe_H_demag_siv(pos2[i])


    #work out total deviation
    diff = Hd1-Hd2

    max_diff = numpy.max(numpy.sqrt(diff[:,0]**2+diff[:,1]**2+diff[:,2]**2))

    print "diff is %30.28g" % max_diff

    return max_diff

  print "test 1: uniform magnetisation"
  m = [1,0,0]
  diff = consistency_check(m)
  nov_2008 =  2.17715631219369855532057703e-09 #15Nov2008, HF, Debian etch
  print "max(diff)=%g (was %g in Nov 2008, delta=%g)" % (diff,nov_2008,diff-nov_2008)
  assert diff <= 3e-9, "failed for m=%s (diff=%s)" % (m,diff)

  print "test 2: varying magnetisation"
  #test 1: uniform magnetisation

  def m((x,y,z)):
    # get access to pi, cos and sin
    import math  
         
    # change angle of Mx and My by 10 degree when x varies by 1nm
    angle = (x/50e-9)*360./360*2*math.pi 
    Mx = math.cos(angle+math.pi/2)
    My = math.sin(angle+math.pi/2)
    Mz = 0
   
    #return magnetisation vector for position (x,y,z)
    return (Mx,My,Mz)


  diff = consistency_check(m)

  nov_2008 =  5.474164841075581810801039769e-09 #15Nov2008, HF, Debian etch
  print "max(diff)=%g (was %g in Nov 2008, delta=%g)" % (diff,nov_2008,diff-nov_2008)
  assert diff <= 6e-9, "failed for m=%s (diff=%s)" % (m,diff)
  
  
def test_demag():
  os.chdir(this_dir)
  out(os.getcwd())
  os.system("make init >make.out 2>&1")
  do_simulation()
  os.chdir(org_dir)

if debug:
  test_demag()
