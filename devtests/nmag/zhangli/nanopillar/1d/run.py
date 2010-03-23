#----------------------------------------------------------------------------
# Values of l (in nm) and j (in 10^10 A/m^2) for which we want
# to do a simulation.
values_of_l_and_j = [(l, j)
                     for l in [20, 25, 30, 35, 40, 45, 50, 55, 60]
                     for j in [1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20]]

discretization = 0.5 # mesh discretization

# We organize things this way:
# For every couple (l, j) we do two simulations: one finds
# the initial configuration (zero current), the second uses it
# for current density = j. Both simulations are performed inside
# a directory with name jXXX_lYYY. This scripts checks what simulations
# have not been done yet and starts one of those.
# If all simulations have been done it exits with 1, otherwise
# exits with 0. This allows to use this script easily on a cluster:
# just launch it as many times as there are nodes in the cluster.
# For better efficiency you might prefer to create a shell script
# to keep the nodes running simulations one after the others.
# The script should look like that:
#
#   #!/bin/bash
#   while true; do
#     nsim run.py --clean &> log.txt
#     if [ $? -eq 1 ]; then
#       exit 0
#     fi
#   done
#
# In fact one needs to launch this script twice for every couple (l, j)!
#----------------------------------------------------------------------------

#--------------------------------------------
#--- Here follows the logic to deal with multiple independent simulations

import os, sys, math, commands

def directory_name(l, j):
    return "j%03d_l%03d" % (int(round(j)), int(round(l)))

initial_m_file = "m0.h5"
main_done_file = "main_done"
preliminary_done_file = "preliminary_done"

all_done = True
for l, j in values_of_l_and_j:
    dn = directory_name(l, j)
    this_main_done_file = os.path.join(dn, main_done_file)
    this_preliminary_done_file = os.path.join(dn, preliminary_done_file)
    this_initial_m_file = os.path.join(dn, initial_m_file)
    main_done = os.path.exists(this_main_done_file)
    preliminary_done = os.path.exists(this_preliminary_done_file)
    have_initial_m = os.path.exists(this_initial_m_file)
    if not preliminary_done:
        if not os.path.isdir(dn):
            os.mkdir(dn)
            print "Created directory '%s': " % dn,
        os.chdir(dn)
        all_done = False
        go_fast = True
        this_l, this_j = l, j
        commands.getoutput("touch %s" % preliminary_done_file)
        print "Starting preliminary zero-current simulation..."
        break
    elif not main_done:
        if have_initial_m:
            os.chdir(dn)
            all_done = False
            go_fast = False
            this_l, this_j = l, j
            commands.getoutput("touch %s" % main_done_file)
            print "Entering directory '%s': starting main simulation..." % dn
            break
        else:
            print ("Skipping '%s': preliminary simulation may be "
                   "still running(?)" % dn)

if all_done: sys.exit(1)

import nmag, nfem
from nmag import SI, mesh

from nsim import sets
from nsim.si_units.si import mu0, Tesla, degrees_per_ns
import nmeshlib.unidmesher as unidmesher

name = "run"
suffix = directory_name(this_l, this_j)
sim_name = name + suffix
llg_damping = SI([0.02, 1.0][go_fast])
j = j*1e10
hl = 0.5*l

if False:
    print "Selecting simulation '%s' in %s" % (name, suffix)
    print "Press a key to start the simulation..."
    raw_input()

#--------------------------------------------
#--- Details about the layers and the materials

mesh_name = "1d"
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
# here, since the magnetisation will continue changing forever
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
                        sim.hysteresis_exit()
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
sim = nmag.Simulation(sim_name, do_demag=False)

# Creates the mesh from the layer structure
mesh_file_name = '%s.nmesh' % mesh_name
if not os.path.exists(mesh_file_name) or new_mesh:
    print "Creating the mesh"
    layers = [(-0.5*l, 0.5*l)]
    mesh_lists = unidmesher.mesh_1d(layers, discretization)
    unidmesher.write_mesh(mesh_lists, out=mesh_file_name)

# Load the mesh
if os.path.exists(mesh_file_name):
    sim.load_mesh(mesh_file_name,
                  [("nanopillar", material)],
                  unit_length=SI(1e-9, "m"))
else:
    raise StandardError,"Need file %s" % mesh_file

sim.set_pinning(pinning)

#--------------------------------------------
## Run the simulation to calculate the hysteresis loop

if go_fast:
    sim.set_m(m0) # Set the initial magnetisation

    # Set additional parameters for the time-integration
    sim.set_params(stopping_dm_dt=1.0*degrees_per_ns,
                   ts_rel_tol=1e-7, ts_abs_tol=1e-7)

    from nsim.when import every, at
    sim.hysteresis([None],
                   save=[('fields', at('stage_end')),
                         ('averages', every('time', SI(5e-12, 's'))),
                         ('restart', at('stage_end') | at('time', SI(100e-12, 's')))],
                   do=[('exit',  at('time', SI(110e-12, 's')))],
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
                   do=[('exit', at('time', SI(50e-9, 's'))),
                       (check_convergence, every(20, 'step'))],
                   convergence_check=every(5, 'step'))
    sys.exit(0)
