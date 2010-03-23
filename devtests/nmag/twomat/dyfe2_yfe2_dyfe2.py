# One dimensional magnetic system studied using nsim
import os, sys, math
import nmag, nfem
from nmag import SI, mesh
from nsim import sets
from nsim.si_units.si import mu0, Tesla, degrees_per_ns
import nmeshlib.unidmesher as unidmesher

#--------------------------------------------
#--- Details about the layers and the materials

sim_name = "dyfe2_yfe2_dyfe2"
# Just to run many simulations without interference (iridis)
sub_name = ""

m_dir = "m_" + sim_name
if not os.path.isdir(m_dir): os.mkdir(m_dir)
m_file = lambda num_stage: "%s/%s.h5" % (m_dir, num_stage)
m0_file = m_file('last')
go_fast = not os.path.exists(m0_file)

llg_damping = SI([0.02, 0.5][go_fast])

# Create the material for Fe2 in DyFe2 and YFe2
# A unique material can be used because the iron moment per unit volume
# in DyFe2 and YFe2 are the same.
# NOTE: The demagnetising field acts as a shape anisotropy in the 1D model:
# H_demag = -M_x which can be expressed as an uniaxial anisotropy
#   H_demag = (2 K_1 m*u) / (mu0*M_sat)
# where the axis u = (1, 0, 0) and K_1 = -mu0*M_sat^2/2
# NOTE: Strictly this is wrong
Ms_Fe2 = SI(0.54861229676e6, "A/m")
uni_anis = nmag.uniaxial_anisotropy(axis=[1, 0, 0], K1=-0.5*mu0*Ms_Fe2**2)
mat_Fe2 = \
  nmag.MagMaterial(name="Fe2",
                   Ms=Ms_Fe2,
                   exchange_coupling=SI(14.6e-12, "J/m"),
                   anisotropy=uni_anis,
                   llg_normalisationfactor=SI(0.001e12, "1/s"),
                   llg_damping=llg_damping,
                   llg_polarisation=SI(1.0))

# Create the material
Ms_DyFe2 = SI(1.18085121013e6, "A/m")
Ms_Dy = Ms_DyFe2 + Ms_Fe2
# the sum comes from taking the data from Jurgen's simulations
# where the total moment in DyFe2 is given Ms_DyFe2 = Ms_Dy - Ms_Fe2
cubic_Dy = \
  nmag.cubic_anisotropy(axis1=[1,0,-1],
                        axis2=[1,0,1],
                        K1=SI(33.853774961e6, "J/m^3"),
                        K2=SI(-16.1710504363e6, "J/m^3"),
                        K3=SI(16.3584237059e6, "J/m^3"))

demag_Dy = nmag.uniaxial_anisotropy(axis=[1, 0, 0], K1=-0.5*mu0*Ms_Dy**2)
mat_Dy = \
  nmag.MagMaterial(name="Dy",
                   Ms=Ms_Dy,
                   exchange_coupling=SI(0.0e-12, "J/m"),
                   anisotropy=demag_Dy + cubic_Dy,
                   llg_normalisationfactor=SI(0.001e12, "1/s"),
                   llg_damping=llg_damping)

#This is the expression returned by the sampler:
#E_anis_Dy=
#    4.23260765 m_Dy(1)^8
#  -11.28695373 m_Dy(0)^2 m_Dy(1)^6
#  - 3.76231791 m_Dy(0)^4 m_Dy(1)^4
#  +15.04927164 m_Dy(0)^6 m_Dy(1)^2
#  + 7.52463582 m_Dy(0)^8
#  -11.26540649 m_Dy(1)^6
#  - 3.67612894 m_Dy(0)^2 m_Dy(1)^4
#  -30.01235432 m_Dy(0)^4 m_Dy(1)^2
#  -15.04927164 m_Dy(0)^6
#  - 1.37590150 m_Dy(1)^4
#  +34.29764228 m_Dy(0)^2 m_Dy(1)^2
#  +26.85919543 m_Dy(0)^4
#  + 4.04535018 m_Dy(1)^2
#  -19.33455961 m_Dy(0)^2
#  + 4.36335016

mesh_name = sim_name
mesh_unit = SI(1e-9, "m")
layers = [(-10.0, -5.0), (-5.0, 5.0), (5.0, 10.0)]
scale = 2.0
B_scale = 1.0/(scale*scale)
mat_allocation = [("DyFe2_up", [mat_Dy, mat_Fe2]),
                  ("YFe2", mat_Fe2),
                  ("DyFe2_down", [mat_Dy, mat_Fe2])]
discretization = 1.0
new_mesh = True

#--------------------------------------------
## The initial configuration and how the applied field should change

# Initial direction for the magnetisation
directions = {'m_Dy':[0,1,0], 'm_Fe2':[0,-1,0]}

def m0_Dy(r):
  return directions['m_Dy']

def m0_Fe(r):
  return directions['m_Fe2']

B_direction = [0.0, 1.0, 0.0] # The direction of the applied field
#The list of values taken by the norm of the applied field
B_norms = [0.1, 0.2, [], 1.0, 1.1, [], 2.0, 2.2, [],
           3.8, 3.82, [], 4.2, 4.25, [], 4.5, 4.6, [],
           5.0, 5.5, [], 8.0]
selected_B_norms = [3.6, 4.0, 4.2]

B_norms = sets.float_set(B_norms, B_scale)
selected_B_norms = sets.float_set(selected_B_norms, B_scale)
layers = [(scale*left, scale*right) for (left, right) in layers]

B_unit = Tesla # The unit for these values

delta_B = 0.0*Tesla

# From the norms and the direction (which is constant) we derive
# all the values that the applied field will take during the simulation
Hs = sets.vector_set(direction=B_direction,
                     norm_list=B_norms,
                     units=B_unit/mu0) # remember that H = B/mu0

# A small deviation to avoid points of unstable equilibrium
H_dev = [SI(0.005e6, "A/m"), 0, SI(0.005e6, "A/m")]
Hs = [[Hi+H_devi for Hi, H_devi in zip(H, H_dev)]
      for H in Hs]

#--------------------------------------------
## The current density for spin-torque calculations

j = [SI(4.22205e12, "A/m^2"), 0.0, 0.0]
j = [0*SI(1e12, "A/m^2"), 0.0, 0.0]

#--------------------------------------------
## Here we set up the simulation

# Create the simulation object
sim = nmag.Simulation(sim_name+sub_name, do_demag=False,
                      adjust_tolerances=False)

# Set the coupling between the two magnetisations
#sim.set_local_magnetic_coupling(mat_Fe2, mat_Dy, SI(-2.2337e-4, "N/A^2"))
sim.set_local_magnetic_coupling(mat_Fe2, mat_Dy, SI(-2.2337e-5, "N/A^2"))

# Creates the mesh from the layer structure
mesh_file_name = '%s.nmesh' % sim_name
if not os.path.exists(mesh_file_name) or new_mesh:
    print "Creating the mesh"
    mesh_lists = unidmesher.mesh_1d(layers, discretization)
    unidmesher.write_mesh(mesh_lists, out=mesh_file_name)

# Load the mesh
if os.path.exists(mesh_file_name):
    sim.load_mesh(mesh_file_name, mat_allocation, unit_length=SI(1e-9, "m"))
else:
    raise StandardError,"Need file %s" % mesh_file

# Set additional parameters for the time-integration
sim.set_params(stopping_dm_dt=5*degrees_per_ns,
               ts_rel_tol=1e-5, ts_abs_tol=1e-5)

num_save = 0
def save_fields_vtk(sim):
    global num_save
    return
    sim.save_fields_vtk("all_fields_%d.vtk" % num_save)
    num_save += 1

#--------------------------------------------
## Run the simulation to calculate the hysteresis loop

if go_fast:
    # Just go rapidly (high damping) to the configuration we want to study
    sim.set_m(m0_Fe, 'm_Fe2') # Set the initial magnetisation
    sim.set_m(m0_Dy, 'm_Dy')

    #sim.set_j(j)  # Set the current density

    from nsim.when import every, at
    save_m = lambda sim: sim.save_restart_file(m_file(sim.stage))
    sim.hysteresis(Hs,
                   save=[ #('fields', every(50, 'step')),
                         ('averages', at('convergence')),
                         (save_m, at('convergence'))],
                   convergence_check=every(5, 'step'))
    sim.save_restart_file(m0_file)

else:
    from nsim.when import every, at

    def min_diff(x_list, x):
        return min([abs(xi - x) for xi in x_list])

    #delta_H = delta_B/mu0
    sim.set_j(j) # Set the current density
    new_Hs = []
    num_H = 0
    for H, this_B_norm in zip(Hs, B_norms):
        #H[1] += delta_H
        #print H[1]*mu0, llg_damping
        num_H += 1
        if min_diff(selected_B_norms, this_B_norm) > 0.00001:
            print "|B| = %s <-- Skipping this!" % this_B_norm
            continue

        print "|B| = %s <-- Starting new stage!" % this_B_norm
        sim.set_m(m_file(num_H)) # Set the initial magnetisation from file
        new_Hs.append(H)
        sim.hysteresis(new_Hs,
                       save=[('averages', at('convergence') | every(100, 'step')),
                             ('fields', every(10000, 'step')),
                             ('restart', every(10000, 'step'))],
                       convergence_check=every(5, 'step'))
