# Matteo Franchin, Dec 2009
# This script runs simulations in order to find at which nanopillar radius
# the coherent state (magnetisation all aligned) becomes unstable in favour
# of the singularity state (magnetisation follows everywhere the surface
# of the nanopillar, developing a singularity in the center of the nanopillar)

from nmag import SI, Simulation, MagMaterial, at
import math, os

# The underlying default state (things that won't change)
default_state = {'nanopillar_length':20.0,
                 'nanopillar_radius':40.0,
                 'discretization':2.0}

# These are actually the different states which we are considering: for each
# state 's' of those a simulation will be performed using as a state
# 'default_state' ``covered'' with 's'.
states = [{'nanopillar_radius': r} for r in [100, 50, 25, 75]]

# For each simulation a different directory is created to avoid interferences
# between them. This function takes the state and returns the corresponding
# directory name.
def directory_from_state(state):
    l = state['nanopillar_length']
    r = state['nanopillar_radius']
    return "l%03d_r%03d" % tuple([l, r])

# This function creates the mesh for the given state.
unit_length = SI(1e-9, 'm') # 1 means 1 nm in the mesh reference frame
def mesh_from_state(state, mesh_file_name):
    state["hl"]  = 0.5*state["nanopillar_length"]
    geo = """
    algebraic3d

    solid nanopillar = cylinder (-$hl$, 0, 0; $hl$, 0, 0; $nanopillar_radius$)
                       and plane (-$hl$, 0, 0; -1, 0, 0)
                       and plane ( $hl$, 0, 0;  1, 0, 0)
                       -maxh=$discretization$;

    tlo nanopillar;
    """

    from nsim.netgen import NetgenMesh
    nm = NetgenMesh()
    nm.set_vars(state)
    nm.geo(geo)
    nm.save(mesh_file_name)

def mesh_name_from_state(state):
    l = state['nanopillar_length']
    r = state['nanopillar_radius']
    return "l%03d_r%03d.nmesh.h5" % tuple([l, r])

def is_already_done(run, this_state):
    return os.path.exists('done')

import nsim.parametric
run = nsim.parametric.ParametricRun(directory_from_state, mesh_from_state,
                                    mesh_name_from_state, is_already_done,
                                    states, default_state)
this_state = run.get_state()

f = open('done', 'w') # We "occupy" the current task!
f.write('done!\n')
f.close()

hl = 0.5*this_state['nanopillar_length']
def m0(p):
    x = min(1.0, max(-1.0, float(SI(p[0], "m")/(hl*unit_length))))
    angle = 0.5*math.pi*x
    return [math.sin(angle), math.cos(angle), 0.0]

def m1(p):
    x, y, z = p
    alpha = \
      0.5*math.pi*min(1.0, max(-1.0, float(SI(x, "m")/(hl*unit_length))))
    R = math.sqrt(y*y + z*z)
    sin_theta = z/R
    cos_theta = y/R
    sin_alpha = math.sin(alpha)
    cos_alpha = math.cos(alpha)
    return [sin_alpha, -cos_alpha*sin_theta, cos_alpha*cos_theta]

# Pinning at the borders
def pinning(p):
    x = float(SI(p[0], "m")/(hl*unit_length))
    if abs(x) >= 0.999:
        return 0.0
    else:
        return 1.0

mat_Py = MagMaterial('Py',
                     Ms=SI(0.86e6, 'A/m'),
                     exchange_coupling=SI(13e-12, 'J/m'))

s = Simulation()

s.load_mesh(run.get_mesh_file_name(),
            [('region1', mat_Py)],
            unit_length=unit_length)

s.set_m(m0)

s.set_pinning(pinning)

s.relax(save=[('fields', at('time', SI(0, 's')) | at('convergence'))])

s.set_m(m1)
s.relax(save=[('fields', at('stage_time', SI(0, 's'))
                         | at('convergence'))])


