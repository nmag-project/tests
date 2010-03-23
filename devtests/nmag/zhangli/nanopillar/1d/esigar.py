# One dimensional magnetic system studied using nsim
import os, sys, math
try:
    import nmag3 as nmag, nfem
    from nmag3 import SI, mesh
except:
    import nmag, nfem
    from nmag import SI, mesh

from nsim import sets
from nsim.si_units.si import mu0, T, degrees_per_ns
import nmeshlib.unidmesher as unidmesher

# We want to perform many simulations at the same time
# This counter allows to select which simulation one wants
# to run, specifying it in the command line. Examples:
#   nsim exch_spring.py 0 --clean
#   nsim exch_spring.py 1 --clean

ss = [0, 4]
if len(sys.argv) > 1:
    for i in range(len(sys.argv)-1):
        try:
            ss[i] = int(sys.argv[i+1])
        except:
            pass

s = ss[0]
s1 = ss[1]
j = p = [0.0, 0.04, 0.06, 0.08, 0.10, 0.12, 0.14, 0.2, 0.02, 0.01, 0.16, 0.18][s]
l = [20, 25, 30, 35, 40, 45, 50, 55, 60, 15, 10][s1]
name = "esigar"
suffix = "_j%03d_l%03d" % (int(round(100*j)), int(round(l)))
same_m0 = True

j = SI(j*1e12, "A/m^2")
midlayer_width = l
extlayer_width = 5.0

w1 = 0.5*(midlayer_width + 2*extlayer_width)
w2 = 0.5*midlayer_width
layers = [(-w1, -w2), (-w2, w2), (w2, w1)]

print "Selecting simulation n. %d; simulation name: %s, %s" % (s, name, suffix)
print "Press a key to start the simulation..."
#raw_input()

sim_name = name + suffix
if same_m0:
    m_dir = "m_" + name
else:
    m_dir = "m_" + name + suffix

if not os.path.isdir(m_dir): os.mkdir(m_dir)
m_file = lambda num_stage: "%s/%s.h5" % (m_dir, num_stage)
m0_file = m_file('last')
go_fast = not os.path.exists(m0_file)

llg_damping = SI([0.02, 1.0][go_fast])

#--------------------------------------------
#--- Details about the layers and the materials

mesh_name = "1d"
#mesh_unit = SI(1e-9, "m")
discretization = 1.0
new_mesh = True

# Create the material for Fe2 in DyFe2 and YFe2
# A unique material can be used because the iron moment per unit volume
# in DyFe2 and YFe2 are the same.
Ms_Fe2 = SI(0.54861229676e6, "A/m")
mat_Fe2 = nmag.MagMaterial(
            name="Fe2",
            Ms=Ms_Fe2,
            exchange_coupling=SI(14.6e-12, "J/m"),
            llg_normalisationfactor=SI(0.001e12, "1/s"),
            llg_damping=SI(llg_damping),
            llg_csi=SI(0.01),
            llg_polarisation=SI(1.0)
          )

# Create the material
Ms_DyFe2 = SI(1.18085121013e6, "A/m")
Ms_Dy = Ms_DyFe2 + Ms_Fe2
# the sum comes from taking the data from Jurgen's simulations
# where the total moment in DyFe2 is given Ms_DyFe2 = Ms_Dy - Ms_Fe2
mat_Dy = nmag.MagMaterial(
           name="Dy",
           Ms=Ms_Dy,
           exchange_coupling=SI(0.0e-12, "J/m"),
           anisotropy=nmag.cubic_anisotropy(
                        axis1=[0, -1, 1],
                        axis2=[0,  1, 1],
                        k1=SI( 33.853774961e6,  "J/m^3"),
                        k2=SI(-16.1710504363e6, "J/m^3"),
                        k3=SI( 16.3584237059e6, "J/m^3")
                      ),
           llg_normalisationfactor=SI(0.001e12, "1/s"),
           llg_damping=llg_damping
         )

mat_allocation = [("hardlayerleft",  [mat_Fe2, mat_Dy]),
                  ("softlayer",       mat_Fe2),
                  ("hardlayerright", [mat_Fe2, mat_Dy])]

#--------------------------------------------
## The initial configuration and how the applied field should change

# Initial direction for the magnetisation
def m0(p, dof_name):
  # Calculate Fe magnetisation m and return -m if dof_name=="Dy"
  x = min(1.0, max(-1.0, float(p[0])/w2))
  angle = 0.5*math.pi*x
  m = [math.sin(angle), math.cos(angle), 0.0]

  if dof_name == "m_Fe2":
    return m
  else:
    return [-mi for mi in m]

H_direction = [0.0, 0.0, 1.0] # The direction of the applied field
# The list of values taken by the norm of the applied field
H_norms = [0.05, 0.1, [], 1.0, 1.1, [], 2.0, 2.2, [],
           3.8, 3.82, [], 4.2, 4.25, [], 4.5, 4.6, [], 5.0]
# Selected norms for the second part of the simulation
H_norms = [0]
selected_H_norms = [0.5, 1.0, 1.5, 2.0, 3.0, 3.2, [], 5.0]
selected_H_norms = [0]

H_scale = 1
H_norms = sets.float_set(H_norms, H_scale)
selected_H_norms = sets.float_set(selected_H_norms, H_scale)

H_unit = T/mu0 # The unit for these values is T (Tesla)

# From the norms and the direction (which is constant) we derive
# all the values that the applied field will take during the simulation
Hs = sets.vector_set(direction=H_direction,
                     norm_list=H_norms)

# A small deviation to avoid points of unstable equilibrium
H_dev = [0.0001, 0.0001, 0.0001]
new_Hs = []
for H in Hs:
    new_Hs.append([Hi+H_devi for Hi, H_devi in zip(H, H_dev)])
    new_Hs.append(H)
Hs = new_Hs

#--------------------------------------------
## Aux. functions

# This function returns a function to set the external field
# We need this because the field acting on iron will be higher
# at borders (non uniform in space).
def H_func(H, H_pinning=[0, 0, 0], H_dev=0.0):
    s = float(H_unit/SI("A/m"))
    def H_func(p, _):
        x = p[0]
        if x >= 0.5*midlayer_width - 1e-5:
            return [s*(Hi + Hpi + H_dev) for Hi, Hpi in zip(H, H_pinning)]
        elif  x <= -0.5*midlayer_width + 1e-5:
            return [s*(Hi - Hpi + H_dev) for Hi, Hpi in zip(H, H_pinning)]
        else: 
            return [s*(Hi + H_dev) for Hi in H]
    return (H_func, SI("A/m"))

#--------------------------------------------
## Here we set up the simulation

# Create the simulation object
sim = nmag.Simulation(sim_name, do_demag=False)

# Set the coupling between the two magnetisations
sim.set_local_magnetic_coupling(mat_Fe2, mat_Dy, SI(-2.2337e-4, "N/A^2"))

# Creates the mesh from the layer structure
mesh_file_name = '%s.nmesh' % mesh_name
if not os.path.exists(mesh_file_name) or new_mesh:
  print "Creating the mesh"
  mesh_lists = unidmesher.mesh_1d(layers, discretization)
  unidmesher.write_mesh(mesh_lists, out=mesh_file_name)

# Load the mesh
if os.path.exists(mesh_file_name):
    sim.load_mesh(mesh_file_name, mat_allocation, unit_length=SI(1e-9, "m"))
else:
    raise StandardError,"Need file %s" % mesh_file

#--------------------------------------------
## Run the simulation to calculate the hysteresis loop

H_funcs = [H_func(H) for H in Hs]

if go_fast:
    # Set additional parameters for the time-integration
    sim.set_timestepper_params(stopping_dm_dt=1.0*degrees_per_ns,
                               rel_tolerance=1e-7, abs_tolerance=1e-7)

    # Just go rapidly (high damping) to the configuration we want to study
    sim.set_m(m0) # Set the initial magnetisation

    sim.set_j([j, 0.0, 0.0])  # Set the current density

    from nsim.when import every, at
    save_m = lambda sim: sim.save_restart_field(m_file(sim.stage))
    sim.hysteresis(H_funcs,
                   save=[('fields', at('convergence') & every(2, 'stage')),
                         ('averages', every('time', SI(5e-12, 's'))),
                         (lambda sim: sys.exit(0), at('time', SI(110e-12, 's'))),
                         (save_m, at('convergence') | at('time', SI(100e-12, 's')))],
                   convergence_check=every(5, 'step'))
    sim.save_restart_field(m0_file)

else:
    # Set additional parameters for the time-integration
    sim.set_timestepper_params(stopping_dm_dt=1e-3*degrees_per_ns,
                               rel_tolerance=1e-7, abs_tolerance=1e-8)

    from nsim.when import every, at

    def min_diff(x_list, x):
        return min([abs(xi - x) for xi in x_list])

    sim.set_j([j, 0.0, 0.0]) # Set the current density
    new_Hs = []
    num_H = 0
    for this_H_norm in H_norms:
        H_idx = 2*num_H + 1
        stage_idx = H_idx + 1
        num_H += 1

        if min_diff(selected_H_norms, this_H_norm) > 1.0e-5:
            print "|B| = %s <-- Skipping this!" % this_H_norm
            continue

        print "|B| = %s <-- Starting new stage!" % this_H_norm
        sim.set_m(m_file(stage_idx)) # Set the initial magnetisation from file
        new_Hs.append(H_funcs[H_idx])
        print Hs[H_idx], H_idx, "out of", len(Hs), "values"

        sim.hysteresis(new_Hs,
                       save=[('averages', every('time', SI(3e-12, 's'))),
                             ('fields', every('time', SI(100e-12, 's'))),
                             ('restart', every(5000, 'step')),
                             (lambda sim: sys.exit(0), at('time', SI(10e-9, 's')))],
                       convergence_check=every(5, 'step'))

