# One dimensional magnetic system studied using nsim
import math, os
import nmag
from nmag import SI, at, every

#--------------------------------------------
#--- Details about the layers and the materials

cubicmesh_bin = "../../../../utils/cubicmesh/cubicmesh"
nmeshpp_bin = "../../../../bin/nmeshpp"

sqside = 12.0
hard_ext_width = 5.0
hard_cent_width = 1.0
soft_width = 20.0
mesh_discret = [0.5, 2.0, 2.0]
mesh_filename = "mesh_i%d_%d_%d_%d_%d.nmesh.h5" \
                % (sqside, hard_ext_width, hard_cent_width, soft_width,
                   mesh_discret[0])

def simulation(sim_name=None, initial_m=None, Hs=[None], save=[], do=[],
               have_j=False, damping_Py=0.01, damping_FePt=0.1):
  if have_j:
    have_j = 1.0
  else:
    have_j = 0.0

  # FeNi, Permalloy
  mat_Py = \
    nmag.MagMaterial(name="Py",
                     Ms=SI(0.86e6, "A/m"),
                     exchange_coupling=SI(13.0e-12, "J/m"),
                     llg_damping=damping_Py,
                     llg_polarisation=have_j*SI(1.0),
                     llg_xi=SI(0.01))

  anis_FePt = \
    nmag.uniaxial_anisotropy(axis=[1, 0, 0],
                             K1=SI(2.5e6, "J/m^3"))

  mat_FePt = \
    nmag.MagMaterial(name="FePt",
                     Ms=SI(1e6, "A/m"),
                     exchange_coupling=SI(10.0e-12, "J/m"),
                     anisotropy=anis_FePt,
                     llg_damping=damping_FePt,
                     llg_polarisation=have_j*SI(1.0),
                     llg_xi=SI(0.01))

  s = nmag.Simulation(sim_name)

  s.set_local_magnetic_coupling(mat_Py, mat_FePt, SI(2.0e-4, "N/A^2"))

  s.load_mesh(mesh_filename,
              [(  "HARD-LEFT", mat_FePt),
               (  "SOFT-LEFT", mat_Py),
               ("HARD-CENTER", mat_FePt),
               ( "SOFT-RIGHT", mat_Py),
               ( "HARD-RIGHT", mat_FePt)],
              unit_length=SI(1e-9, "m"))

  if type(initial_m) == str:          # Set the initial magnetisation
    s.load_m_from_h5file(initial_m)   # a) from file if a string is provided

  else:
    s.set_m(initial_m[0], 'm_Py')
    s.set_m(initial_m[1], 'm_FePt')

  s.hysteresis(Hs, save=save, do=do, convergence_check=every(5, 'step'))
  return s

def exec_sh(cmd):
  import commands
  print "EXECUTING: %s" % cmd
  print "BEGIN OUTPUT\n%s\nEND OUTPUT\n" % commands.getoutput(cmd)

# Create the mesh
if not os.path.exists(mesh_filename):
  l = 2*hard_ext_width + 2*soft_width + hard_cent_width
  dl = int(round(l/mesh_discret[0]))
  dw = int(round(sqside/mesh_discret[1]))
  mesh_spec = "%s:%s,%s:%s,%s:%s" % (l, dl, sqside, dw,  sqside, dw)
  mesh_regions = "x:%s,%s,%s,%s" % (hard_ext_width,
                                    hard_ext_width+soft_width,
                                    hard_ext_width+soft_width+hard_cent_width,
                                    hard_ext_width+2*soft_width+hard_cent_width)

  exec_sh("%s mesh.nmesh,%s %s" % (cubicmesh_bin, mesh_spec, mesh_regions))
  exec_sh("%s -c mesh.nmesh %s" % (nmeshpp_bin, mesh_filename))
  exec_sh("rm -f mesh.nmesh m0.h5")

# If the initial magnetisation has not been calculated and saved into
# the file relaxed_m_file, then do it now!
relaxed_m_file = "m0.h5"
if not os.path.exists(relaxed_m_file):
  x0 = hard_ext_width*1e-9
  x1 = (hard_ext_width + soft_width)*1e-9
  print x0, x1

  def m0_Py(r):
    x = r[0]
    u = min(1.0, max(0.0, (x - x0)/(x1 - x0)))
    angle = math.pi*(1.0 - u)
    return [math.cos(angle), math.sin(angle), 0]

  def m0_FePt(r):
    return m0_Py(r)

  def save_m(s):
    s.save_restart_file(relaxed_m_file)

  s = simulation(sim_name="relax",
                 damping_Py=1.0,
                 damping_FePt=1.0,
                 initial_m=[m0_Py, m0_FePt],
                 save=[('averages', every(1000, 'step')),
                       ('fields', at('step', 0) | at('stage_end'))],
                 do=[(save_m, at('stage_end'))])
  del s

def set_current(j):
    def j_setter(sim):
        sim.set_current_density([j, 0.0, 0.0], unit=SI("A/m^2"))
    return j_setter


ns = SI(1e-9, 's')
simulation(sim_name="stt",
           initial_m=relaxed_m_file,
           have_j=True,
           save=[('averages', every('time', SI(0.05e-9, 's'))),
                 ('fields', every('time', SI(1e-9, 's')))],
           do=[(set_current(-0.2e12), at('time', 5*ns)),
               (set_current(0), at('time', 7*ns)),
               (set_current(0.2e12), at('time', 12*ns)),
               (set_current(0), at('time', 14*ns)),
               ('exit', at('time', SI(20e-9, 's')))])

