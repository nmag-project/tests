# Nmag example: briefly describe what it does

import os, sys, math
from nmag.common import *
from nmag import vector_set

import ocaml

# In dynamics simulations it is often necessary to first compute the initial
# state and then proceed with the real dynamics simulation. We have to carry
# out two simulations! The first one serves to compute the initial
# magnetisation state which is stored in the following file,
relaxed_m_file = "m0.h5"

# In the second simulation we have to load this file and study the dynamics.
# This is just one script, but it will be used to carry out both parts.
# We do the relaxation only if 'relaxed_m_file' doesn't exist. Makes sense,
# right?
if not os.path.exists(relaxed_m_file):
    simulation_name = 'relaxation'
else:
    simulation_name = 'run'

# It is then desirable to use different damping constants for the two
# simulations. 
if simulation_name == 'relaxation':
    damping = 0.5   # High damping if we are just relaxing
else:
    damping = 0.01  # Realistic damping when studying the dynamics 

#def build_simulation_object(damping=0.5):
mat_Py = MagMaterial(name='Py',
                     Ms=SI(0.86e6, 'A/m'),
                     llg_damping=damping, # <--- Here we use the damping!
                     llg_gamma_G=SI(2.210173e5, "m/A s"),
                     exchange_coupling=SI(13.0e-12, 'J/m'))

s = Simulation(simulation_name)

s.load_mesh("mesh.nmesh.h5", [('Py', mat_Py)], unit_length=SI(1e-9, 'm'))

# We do the relaxation, if needed
if simulation_name == 'relaxation':
    s.set_m([1, 0, 0])
    s.relax()
    s.save_restart_file(relaxed_m_file)
    # Exit right now, we don't want to proceed with damping 0.5!
    sys.exit(0)

else:
    # Otherwise we just load the magnetisation from file
    s.load_m_from_h5file(relaxed_m_file)

# Here we add a time dependent field
def update_H_ext(t_su):
    t = SI(1e-12, 's')*t_su
    GHz = 1e9/SI('s')
    frequency = 10*GHz
    amplitude = math.sin(float(math.pi*frequency*t))
    fieldname = 'H_ext'
    s._fields.set_subfield(None, # subfieldname
                           [0, amplitude, 0],
                           SI(0.4e6, 'A/m'),
                           fieldname=fieldname,
                           auto_normalise=False)
    (mwe, field) = s._master_mwes_and_fields_by_name[fieldname]
    ocaml.lam_set_field(s._lam, field, "v_" + fieldname)
    print "*",

s.pre_rhs_funs.append(update_H_ext)

# Then study the dynamics when a field is applied: here we study the switching
# dynamics.
s.set_params(stopping_dm_dt=0) # Never stop for convergence
s.relax(save=[('averages', every('time', SI(2.5e-12, 's'))),
              ('fields', every('time', SI(100e-12, 's')))],
        do=[('exit', at('stage_time', SI(1e-9, 's')))])
        # ^^^ exit after 10 ns

