import os, sys, commands, math

examesh_bin="../../../../../../utils/cubicmesh/examesh"
# The underlying default state (things that won't change)
default_state = {'lx':100.0, 'ly':100.0, 'lz':10.0, 'ratio_nz_nx':0.1}
use_hlib = True

# These are actually the different states which we are considering: for each
# state 's' of those a simulation will be performed using as a state
# 'default_state' ``covered'' with 's'.
states = [{'nx':nx} for nx in [64, 51, 41]]

def sizes(state):
    nx = state['nx']
    ratio_nz_nx = state['ratio_nz_nx']
    ny = int(round(nx * 2/math.sqrt(3)))
    nz = int(nx * ratio_nz_nx)
    lx, ly, lz = [state[L] for L in ["lx", "ly", "lz"]]
    return [(lx, nx), (ly, ny), (lz, nz)]

def max_rod_length(state):
    (lx, nx), (ly, ny), (lz, nz) = s = sizes(state)
    dx, dy, dz = [li/ni for li, ni in s]
    u = max(dx, math.sqrt((0.5*dx)**2 + dy**2))
    return math.sqrt(u*u + dz*dz)

# For each simulation a different directory is created to avoid interferences
# between them. This function takes the state and returns the corresponding
# directory name.
def directory_from_state(state):
    return "maxrod%.2f" % max_rod_length(state)

# Different state may (or may not) require different meshes. This function
# returns the name of the mesh which should be used by the simulation
# with state 'state'. If this function returns always the same name for all
# the provided 'states', then just a mesh will be created.
def mesh_name_from_state(state):
    return "maxrod%.2f.nmesh.h5" % max_rod_length(state)

# This function creates the mesh for the given state.
def mesh_from_state(state, mesh_file_name):
    (lx, nx), (ly, ny), (lz, nz) = s = sizes(state)
    spec = "%d:%d,%d:%d,%d:%d" % (lx, nx, ly, ny, lz, nz)
    print commands.getoutput("../%s %s,%s" % (examesh_bin, mesh_file_name, spec))

# File used to signal the current status of a simulation
preliminary_done_file = "preliminary_done"
main_done_file = "main_done"
initial_m_file = "relax_restart.h5"

# This function is used to decide whether a simulation has been already
# started or not. If the function returns True, then the current state
# will be chosen for starting the next simulation. If it returns False
# then the following state will be considered. This function is called
# from within the directory where the simulation should be (eventually)
# started.
def is_already_done(run, state):
    main_done = os.path.exists(main_done_file)
    preliminary_done = os.path.exists(preliminary_done_file)
    have_initial_m = os.path.exists(initial_m_file)
    import commands
    if not preliminary_done:
        state['preliminary'] = True
        commands.getoutput("touch %s" % preliminary_done_file)
        print "Starting preliminary simulation..."
        return False

    elif not main_done:
        if have_initial_m:
            state['preliminary'] = False
            commands.getoutput("touch %s" % main_done_file)
            print "starting main simulation..."
            return False
        else:
            print "%s missing???" % initial_m_file
            return True
    else:
        print ("Skipping '%s': preliminary simulation may be "
                "still running(?)" % run.get_directory_name())
        return True
 
#----------------------------------------------------------------------------
import nsim.parametric
run = nsim.parametric.ParametricRun(directory_from_state, mesh_from_state,
                                    mesh_name_from_state, is_already_done,
                                    states, default_state)
this_state = run.get_state()
(lx, nx), (ly, ny), (lz, nz) = sizes(this_state)
mesh_file_name = run.get_mesh_file_name()
suffix = run.get_directory_name()

preliminary = this_state['preliminary']








# Reduced standard problem for spin-transfer torque (Zhang-Li model)
# We model a bar 100 nm x 100 nm x 10 nm where a vortex sits
# in the center. We study the reaction of the vortex to the
# application of an electric current.
#
import nmag
from nmag import SI, mesh
from nsim.when import every, at
from nsim.si_units.si import mu0, Tesla, degrees_per_ns


if use_hlib:
    ocaml.init_hlib("/rhome/franchin/nmag-0.1/lib/libhmatrix-1.3.so")

    # HLib default parameters
    hp = {}
    hp['nfdeg'] = 4
    hp['nmin'] = 20
    hp['p'] = 4
    hp['eta'] = 2.0
    hp['eps'] = 0.0001

restart_file = "relax_restart.h5"
if not os.path.exists(restart_file):
  llg_damping = 1.0
  llg_xi = 0.0
  j = 0 # A/m^2
  llg_polarisation = 0.0
  stopping_dm_dt = (0.01*180/math.pi) * degrees_per_ns
  sim_name = "relax"
  save = [('averages', every(1000, 'step') | at('convergence')),
          ('restart', at('stage_end')), ('fields', at('step', 0))]
  do = [('exit', at("time", SI(5e-9, "s")))]

else:
  llg_damping = 0.1
  llg_xi = 0.05
  j = 1e12 # A/m^2
  llg_polarisation = 1.0
  stopping_dm_dt=0.0
  sim_name = "stt"
  save = [('fields', at('convergence') | every('time', SI(1.0e-9, "s"))),
          ('averages', every('time', SI(0.05e-9, "s")) | at('stage_end')),
          ('restart', every('time', SI(0.25e-9, "s")))]
  do = [('exit', at("time", SI(16e-9, "s")))]


width_factor = 1.0
j *= width_factor
exchange_coupling = width_factor*SI(13.0e-12, "J/m")
Ms = SI(0.8e6,"A/m")*width_factor
mat_Py = nmag.MagMaterial(name="Py",
                          Ms=Ms,
                          exchange_coupling=exchange_coupling,
                          llg_gamma_G=SI(0.2211e6, "m/A s"),
                          llg_polarisation=llg_polarisation,
                          llg_xi=llg_xi,
                          llg_damping=llg_damping,
                          llg_normalisationfactor=SI(0.1e12, "s^(-1)"))

if use_hlib:
    sim = nmag.Simulation(sim_name, use_hlib=True, use_pvode=True, hlib_params=hp)
else:
    sim = nmag.Simulation(sim_name, use_pvode=True)

sim.load_mesh(mesh_file_name, [("Py", mat_Py)],
              unit_length=SI(1e-9,"m"))

c = [50.0e-9, 50.0e-9, 5.0e-9] # The center of the body
def m(p):
  v = [pi - ci for pi, ci in zip(p, c)]
  vo = [-v[1], v[0], 40.0e-9]
  # m will return a non normalized vector, nsim will normalize it anyway
  return vo

if j != 0.0:
  sim.load_m_from_h5file(restart_file)
  sim.set_current_density([j, 0, 0])
else:
  sim.set_m(m)

sim.set_params(ts_rel_tol=1e-07,
               ts_abs_tol=1e-07,
               stopping_dm_dt=stopping_dm_dt)

sim.relax(save=save, do=do)

