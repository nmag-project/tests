"""
Simulation of domain wall in constrained nanopillars for different nanopillar
geometries.

We organize things this way: for every couple state we do two simulations:
one finds the initial configuration (zero current), the second uses it
for current density = j. Both simulations are performed inside a directory
with name jXXX_lYYY. This scripts checks what simulations have not been done
yet and starts one of those. If all simulations have been done it exits
with exit-status 1, otherwise exits with 0. This allows to use this script
easily on a cluster: just launch it as many times as there are nodes in the
cluster. For better usability you might prefer to create a shell script
to keep the nodes running simulations one after the others.
The script should look like that:

  #!/bin/bash
  while true; do
    nsim run.py --clean &> log.txt
    if [ $? -eq 1 ]; then
      exit 0
    fi
  done
"""

import os, sys, commands

# The underlying default state (things that won't change)
default_state = {'nanopillar_length':20.0,
                 'nanopillar_side_y':10.0, 'nanopillar_side_z':10.0,
                 'discretization':3.0, 'current_density':40.0,
                 'use_demag':True}

# These are actually the different states which we are considering: for each
# state 's' of those a simulation will be performed using as a state
# 'default_state' ``covered'' with 's'.
states = [{'nanopillar_side_y':y} for y in [13]]

# For each simulation a different directory is created to avoid interferences
# between them. This function takes the state and returns the corresponding
# directory name.
def directory_from_state(state):
    l = state['nanopillar_length']
    y = state['nanopillar_side_y']
    z = state['nanopillar_side_z']
    j = state['current_density']
    return "j%03d_l%03d_y%03d_z%03d" % tuple([int(round(j)), l, y, z])

# Different state may (or may not) require different meshes. This function
# returns the name of the mesh which should be used by the simulation
# with state 'state'. If this function returns always the same name for all
# the provided 'states', then just a mesh will be created.
def mesh_name_from_state(state):
    l = state['nanopillar_length']
    y = state['nanopillar_side_y']
    z = state['nanopillar_side_z']
    j = state['current_density']
    return "l%03d_y%03d_z%03d.nmesh.h5" % tuple([l, y, z])

# This function creates the mesh for the given state.
def mesh_from_state(state, mesh_file_name):
    state["hl"]  = 0.5*state["nanopillar_length"]
    state["hsy"] = 0.5*state["nanopillar_side_y"]
    state["hsz"] = 0.5*state["nanopillar_side_z"]
    geo = """
    algebraic3d

    solid nanopillar = orthobrick (-$hl$, -$hsy$, -$hsz$; $hl$, $hsy$, $hsz$)
                       -maxh=$discretization$;
    tlo nanopillar;
    """

    from nsim.netgen import NetgenMesh
    nm = NetgenMesh()
    nm.set_vars(state)
    nm.geo(geo)
    nm.save(mesh_file_name)


# File used to signal the current status of a simulation
initial_m_file = "m0.h5"
main_done_file = "main_done"
preliminary_done_file = "preliminary_done"

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
mesh_file_name = run.get_mesh_file_name()
suffix = run.get_directory_name()

l = this_state['nanopillar_length']
j = this_state['current_density']
preliminary = this_state['preliminary']

import nmag, nfem
from nmag import SI, mesh

from nsim import sets
from nsim.si_units.si import mu0, Tesla, degrees_per_ns
import nmeshlib.unidmesher as unidmesher
import math

name = "run"
sim_name = name + suffix
llg_damping = SI([0.02, 1.0][preliminary])
j = j*1e10
hl = 0.5*l

if False:
    print "Selecting simulation '%s' in %s" % (name, suffix)
    print "Press a key to start the simulation..."
    raw_input()

#--------------------------------------------
#--- Details about the layers and the materials

mesh_unit = SI(1e-9, "m")
new_mesh = True

material = nmag.MagMaterial(
            name="mat",
            Ms=SI(0.8e6, "A/m"),
            exchange_coupling=SI(13.0e-12, "J/m"),
            llg_normalisationfactor=SI(0.001e12, "1/s"),
            llg_damping=SI(llg_damping),
            llg_xi=SI(0.01),
            llg_polarisation=SI(1.0))

#--------------------------------------------
## The initial configuration and how the applied field should change

# Initial direction for the magnetisation
def m0(p):
    # Calculate Fe magnetisation m and return -m if dof_name=="Dy"
    x = min(1.0, max(-1.0, float(SI(p[0], "m")/(mesh_unit*hl))))
    angle = 0.5*math.pi*x
    return [math.sin(angle), math.cos(angle), 0.0]

# Pinning at the borders
def pinning(p):
    x = float(SI(p[0], "m")/(mesh_unit*hl))
    if abs(x) >= 0.999:
        return 0.0
    else:
        return 1.0

#--------------------------------------------
## Here we implement an ad-hoc check for convergence
# Usually, in hysteresis loop computations, we stop when dm/dt becomes
# small everywhere. This does not make any sense for the problem considered
# here, since the magnetisation will continue to change forever
# (we get a stationary precession). We therefore use another criterion
# to stop the simulation: we stop when the change of the rotation frequency
# for the mean magnetisation becomes lower than a given limit.

old_phi_t = None
old_omega_t = None
countdown0 = 5
countdown = countdown0
stopping_domega_dt = 1e-3 # in GHz/ns
def check_convergence(sim):
    global old_phi_t, old_omega_t, countdown
    mx, my, mz = sim.get_subfield_average_siv("m", "mat")
    t = sim.time
    m = math.sqrt(mx*mx + my*my + mz*mz)
    if m > 0.0:
        m_ort = math.sqrt(my*my + mz*mz)
        phi = math.atan2(mz, my)
        theta = math.acos(mx/m)
        if old_phi_t != None:
            old_phi, old_t = old_phi_t
            dphi = phi - old_phi
            if dphi > math.pi:
                old_phi += 2.0*math.pi
            if dphi < -math.pi:
                old_phi -= 2.0*math.pi
            dphi = phi - old_phi
            dt = t - old_t
            dphi_dt = dphi/dt
            omega = dphi_dt/(2.0*math.pi)
            if old_omega_t != None:
                old_omega, old_t = old_omega_t
                domega = old_omega - omega
                dt = old_t - t
                domega_dt = domega/dt
                ps = SI(1e-12, "s")
                GHz_per_ns = SI(1e18, "1/s^2")
                GHz = SI(1e9, "1/s")
                t_nu = float(t/ps)
                omega_nu = float(omega/GHz)
                domega_dt_nu = float(domega_dt/GHz_per_ns)
                if abs(domega_dt_nu) < stopping_domega_dt:
                    countdown -= 1
                    if countdown < 0:
                        print "CONVERGED"
                        f = open("../freqs.dat", "a")
                        f.write("%s %s %s %s %s %s %s %s\n"
                                % (this_l, this_j, t_nu, omega_nu,
                                   domega_dt_nu, mx, my, mz))
                        f.close()
                        #sim.hysteresis_exit()
                else:
                    countdown = countdown0
                f = open("freq.dat", "a")
                f.write("%s %s %s %s %s %s\n"
                        % (t_nu, omega_nu, domega_dt_nu, mx, my, mz))
                f.close()
            old_omega_t = (omega, t)
        old_phi_t = (phi, t)


#--------------------------------------------
## Here we set up the simulation

# Create the simulation object
sim = nmag.Simulation(sim_name, do_demag=this_state['use_demag'])

# Load the mesh
if os.path.exists(mesh_file_name):
    sim.load_mesh(mesh_file_name,
                  [("nanopillar", material)],
                  unit_length=SI(1e-9, "m"))
else:
    raise StandardError,"Need file %s" % mesh_file_name

sim.set_pinning(pinning)

#--------------------------------------------
## Run the simulation to calculate the hysteresis loop

if preliminary:
    sim.set_m(m0) # Set the initial magnetisation

    # Set additional parameters for the time-integration
    sim.set_params(stopping_dm_dt=1.0*degrees_per_ns,
                   ts_rel_tol=1e-7, ts_abs_tol=1e-7)

    from nsim.when import every, at
    sim.hysteresis([None],
                   save=[('fields', at('stage_end')),
                         ('averages', every('time', SI(5e-12, 's'))),
                         ('restart', at('stage_end') | at('time', SI(100e-12, 's')))],
                   do=[('exit',  at('time', SI(5000e-12, 's')))],
                   convergence_check=every(5, 'step'))
    commands.getoutput("mv *_restart.h5 %s" % initial_m_file)
    sys.exit(0)

else:
    sim.load_m_from_h5file(initial_m_file)
    sim.set_current_density([j, 0.0, 0.0])

    # Set additional parameters for the time-integration
    sim.set_params(stopping_dm_dt=0.0*degrees_per_ns,
                   ts_rel_tol=1e-7, ts_abs_tol=1e-7)

    from nsim.when import every, at

    sim.hysteresis([None],
                   save=[('averages', every('time', SI(9e-12, 's'))),
                         ('fields', every('time', SI(1.0e-9, 's'))),
                         ('restart', every(5000, 'step'))],
                   do=[('exit', at('time', SI(15e-9, 's'))),
                       (check_convergence, every(20, 'step'))],
                   convergence_check=every(5, 'step'))
    sys.exit(0)

