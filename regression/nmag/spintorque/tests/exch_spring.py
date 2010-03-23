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

s = 0
if len(sys.argv) > 1:
    for arg in sys.argv:
        try:
            s = int(arg)
            break
        except:
            pass

print "Selecting simulation n.", s

xi = [0.01, 0.02, 0.03, 0.04][s]
sim_name = "exch_spring_xi%02d" % (100*xi)


#--------------------------------------------
#--- Details about the layers and the materials

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
mat_Fe2 = nmag.MagMaterial(
           name="Fe2",
           Ms=Ms_Fe2,
           exchange_coupling=SI(14.6e-12, "J/m"),
           llg_normalisationfactor=SI(0.001e12, "1/s"),
           llg_damping=llg_damping,
           llg_csi=SI(xi),
           llg_polarisation=SI(1.0))

mesh_name = sim_name
mesh_unit = SI(1e-9, "m")
midlayer_width = 80.0
extlayer_width = 40.0

w1 = 0.5*(midlayer_width + 2*extlayer_width)
w2 = 0.5*midlayer_width
layers = [(-w1, w1)]

H_scale = 1.0/64.0
mat_allocation = [("YFe2", mat_Fe2)]
discretization = 0.25
new_mesh = True

#--------------------------------------------
## The initial configuration and how the applied field should change

# Initial direction for the magnetisation
m0 = [0, -1, 0]

H_direction = [0.0, 1.0, 0.0] # The direction of the applied field
#The list of values taken by the norm of the applied field
H_norms = [0.05, 0.1, [], 1.0, 1.1, [], 2.0, 2.2, [],
           3.8, 3.82, [], 4.2, 4.25, [], 4.5, 4.6, [],
           5.0, 5.5, [], 8.0]
selected_H_norms = [3.6, 4.0, 4.2]

H_norms = sets.float_set(H_norms, H_scale)
selected_H_norms = sets.float_set(selected_H_norms, H_scale)
#print H_norms[32]
#sys.exit(0)

H_unit = T/mu0 # The unit for these values is T (Tesla)

# From the norms and the direction (which is constant) we derive
# all the values that the applied field will take during the simulation
Hs = sets.vector_set(direction=H_direction,
                     norm_list=H_norms)

# A small deviation to avoid points of unstable equilibrium
H_dev = [0.0001, 0, 0.0001]
Hs = [[Hi+H_devi for Hi, H_devi in zip(H, H_dev)]
      for H in Hs]

H_pinning_norm = -10.0
H_pinning, = sets.vector_set(direction=H_direction,
                             norm_list=[H_pinning_norm])

#--------------------------------------------
## The current density for spin-torque calculations

j = [SI(4e12, "A/m^2"), 0.0, 0.0]

#--------------------------------------------
## Aux. functions

# This function returns a function to set the external field
# We need this because the field acting on iron will be higher
# at borders.
def H_func(H, H_pinning):
    s = float(H_unit/SI("A/m"))
    def H_func((x,), _):
        if abs(x) < 0.5*midlayer_width:
            return [s*Hi for Hi in H]
        else:
            return [s*(Hi + Hpi) for Hi, Hpi in zip(H, H_pinning)]
    return (H_func, SI("A/m"))

#--------------------------------------------
## Here we set up the simulation

# Create the simulation object
sim = nmag.Simulation(sim_name, do_demag=False)

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

#--------------------------------------------
## Run the simulation to calculate the hysteresis loop

H_funcs = [H_func(H, H_pinning) for H in Hs]

if go_fast:
    # Set additional parameters for the time-integration
    sim.set_timestepper_params(stopping_dm_dt=0.1*degrees_per_ns,
                               rel_tolerance=1e-7, abs_tolerance=1e-9)

    # Just go rapidly (high damping) to the configuration we want to study
    sim.set_m(m0) # Set the initial magnetisation

    sim.set_j(j)  # Set the current density

    from nsim.when import every, at
    save_m = lambda sim: sim.save_restart_field(m_file(sim.stage))
    sim.hysteresis(H_funcs,
                   save=[('fields', at('convergence'))],
                   convergence_check=every(5, 'step'))
    sim.save_restart_field(m0_file)

else:
    # Set additional parameters for the time-integration
    sim.set_timestepper_params(stopping_dm_dt=5*degrees_per_ns,
                               rel_tolerance=1e-7, abs_tolerance=1e-8)

    from nsim.when import every, at

    def min_diff(x_list, x):
        return min([abs(xi - x) for xi in x_list])

    sim.set_j(j) # Set the current density
    new_Hs = []
    num_H = 0
    for H, this_H_norm in zip(H_funcs, H_norms):
        #H[1] += delta_H
        #print H[1]*mu0, llg_damping
        num_H += 1
        if min_diff(selected_H_norms, this_H_norm) > 0.00001:
            print "|B| = %s <-- Skipping this!" % this_H_norm
            continue

        print "|B| = %s <-- Starting new stage!" % this_H_norm
        sim.set_m(m_file(num_H)) # Set the initial magnetisation from file
        new_Hs.append(H)
        sim.hysteresis(new_Hs,
                       save=[('averages', at('convergence') | every(100, 'step')),
                             ('fields', every(10000, 'step')),
                             ('restart', every(10000, 'step'))],
                       convergence_check=every(5, 'step'))
