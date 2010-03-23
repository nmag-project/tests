# One dimensional magnetic system studied using nsim
import os, sys, math
import nmag, nfem
from nmag import SI, mesh
from nsim.si_units.si import mu0, Tesla
import nmeshlib.unidmesher as unidmesher

def m_file(stage, directory="m_configs"):
  """Returns the name of the file containing the magnetisation configuration
  with name 'stage'
  """
  m_dir = directory # Directory where to save the magnetisation
  if not os.path.isdir(m_dir): os.mkdir(m_dir)
  return "%s/%s.h5" % (m_dir, stage)

def m_dyn_file(H, directory="m_dyns"):
  """Returns the name of the file containing the magnetisation evolution
  as a function of time.
  """
  hi = (list(H))[2]
  hi_str = "%05d" % int(round(float((100*hi*SI("A/m")*mu0/Tesla))))
  m_dir = directory # Directory where to save the magnetisation
  if not os.path.isdir(m_dir): os.mkdir(m_dir)
  return "%s/h%s.dat" % (m_dir, hi_str)

# Function used to write the evolution of the magnetisation
def save_averages(sim):
  time = float(sim.time/SI(1e-12, "s"))
  H = sim.get_subfield_average_siv("H_ext")
  hx, hy, hz = H
  mfx, mfy, mfz = sim.get_subfield_average_siv("m", "Fe2")
  mdx, mdy, mdz = sim.get_subfield_average_siv("m", "Dy")
  out_data = [time, hx, hy, hz, mfx, mfy, mfz, mdx, mdy, mdz]
  out_line = " ".join(["%s" % number for number in out_data])

  f = open(m_dyn_file(H), "a")
  f.write(out_line + "\n")
  f.close()

class DyFe2_YFe2_DyFe2:
  def __init__(self, sim_name, damping, enable_demag=1.0,
               norm_factor=0.001e12, width_soft=10.0, width_hard=5.0,
               width_unit=SI(1e-9, "m")):
    self.sim_name = sim_name
    self.damping = damping
    self.enable_demag = enable_demag
    self.norm_factor = norm_factor

    self.Ms_Fe2 = SI(0.54861229676e6, "A/m")
    self.A_Fe2 = SI(14.6e-12, "J/m")
    self.A_lc = SI(-2.0e-4, "N/A^2")

    self.Ms_DyFe2 = SI(1.18085121013e6, "A/m")
    self.Ms_Dy = self.Ms_DyFe2 + self.Ms_Fe2

    # Here we try to arrange the mesh such that the discretization cell
    # is exactly in the middle of the soft-hard boundary.
    # This is the most accurate way to render correctly the length
    # of the soft layer.
    self.discretization = 0.125
    n = int(round(width_hard/self.discretization))
    d = width_hard/(n + 0.5)
    self.width_hard = n*d
    self.width_soft = width_soft + d
    self.discretization = d
    self.mesh_file_name = '%s.nmesh' % sim_name
    self.width_unit = width_unit
    self.new_mesh = True

    self.sim = None

  def setup(self):
    nf = self.norm_factor

    # Create the material for Fe2 in DyFe2 and YFe2
    # A unique material can be used because the iron moment per unit volume
    # in DyFe2 and YFe2 are the same.
    # NOTE: The demagnetising field acts as a shape anisotropy in the 1D model:
    # H_demag = -M_x which can be expressed as an uniaxial anisotropy
    #   H_demag = (2 K_1 m*u) / (mu0*M_sat)
    # where the axis u = (1, 0, 0) and K_1 = -mu0*M_sat^2/2
    # NOTE: Strictly this is wrong
    demag_Fe2 = \
      nmag.uniaxial_anisotropy(axis=[1, 0, 0],
                               K1=-self.enable_demag*0.5*mu0*self.Ms_Fe2**2)
    mat_Fe2 = \
      nmag.MagMaterial(name="Fe2",
                       Ms=self.Ms_Fe2,
                       exchange_coupling=self.A_Fe2,
                       anisotropy=demag_Fe2,
                       llg_normalisationfactor=SI(nf, "1/s"),
                       llg_damping=SI(self.damping),
                       llg_polarisation=SI(1.0))

    # Create the material
    # the sum comes from taking the data from Jurgen's simulations
    # where the total moment in DyFe2 is given Ms_DyFe2 = Ms_Dy - Ms_Fe2
    cubic_Dy = \
      nmag.cubic_anisotropy(axis1=[1, -1, 0],
                            axis2=[1,  1, 0],
                            K1=SI(33.853774961e6, "J/m^3"),
                            K2=SI(-16.1710504363e6, "J/m^3"),
                            K3=SI(16.3584237059e6, "J/m^3"))

    demag_Dy = \
      nmag.uniaxial_anisotropy(axis=[1, 0, 0],
                               K1=-self.enable_demag*0.5*mu0*self.Ms_Dy**2)
    mat_Dy = \
      nmag.MagMaterial(name="Dy",
                       Ms=self.Ms_Dy,
                       exchange_coupling=SI(0.0e-12, "J/m"),
                       anisotropy=demag_Dy + cubic_Dy,
                       llg_normalisationfactor=SI(nf, "1/s"),
                       llg_damping=SI(self.damping))

    #--------------------------------------------
    ## Here we set up the simulation

    # Create the simulation object
    sim = nmag.Simulation(self.sim_name, do_demag=False,
                          adjust_tolerances=False)

    # Set the coupling between the two magnetisations
    #sim.set_local_magnetic_coupling(mat_Fe2, mat_Dy, SI(-2.2337e-4, "N/A^2"))
    sim.set_local_magnetic_coupling(mat_Fe2, mat_Dy, self.A_lc)

    x0 = self.width_soft*0.5
    x1 = x0 + self.width_hard
    layers = [(-x1, -x0), (-x0, x0), (x0, x1)]
    mat_allocation = [("DyFe2_up", [mat_Dy, mat_Fe2]),
                      ("YFe2", mat_Fe2),
                      ("DyFe2_down", [mat_Dy, mat_Fe2])]

    # Creates the mesh from the layer structure
    if not os.path.exists(self.mesh_file_name) or self.new_mesh:
        print "Creating the mesh"
        mesh_lists = unidmesher.mesh_1d(layers, self.discretization)
        unidmesher.write_mesh(mesh_lists, out=self.mesh_file_name)
    sim.load_mesh(self.mesh_file_name, mat_allocation, unit_length=SI(1e-9, "m"))

    self.sim = sim
    return sim
