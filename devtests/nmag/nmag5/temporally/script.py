import os, sys, math, numpy
from nmag import SI, every, at, MagMaterial, Simulation, default_hmatrix_setup
from nmag.constants import Oe, degrees_per_ns

ps = SI(1e-12, "s"); Hz = 1/SI("s"); GHz = 1e9*Hz; nm = 1e-9*SI("m")

m0 = [1, 0, 0]                        # Initial magnetisation
H_strength = 1000*Oe                  # Bias field strength
bias_H = [H_strength, 0*Oe, 0*Oe]     # Bias field vector

dmdt = SI(1745329.2519943293, '1/s')  # Stopping dm/dt for relaxation
relaxed_start_file='relaxed.h5'       # Where to save the ground state

# Pulse parameters
pulse = [0.0, 0.0, 1.0]               # Pulse field direction
frequency = 30                        # Maximum frequency of Sinc (GHz)
sinc_amplitude = 10*Oe                # Pulse amplitude
sinc_t0 = float((10.0/(2*frequency))*1000)
sinc_omega = 30*GHz * 2*math.pi

def setup_simulation(name, damping, demag_tol=1.0, pc_tol=1.0):
    '''Script to create the simulation object (to be used both for relaxation
    and for the dynamics).'''
    mat_Py = MagMaterial(name="Py",
                         Ms=SI(0.8e6,"A/m"),
                         exchange_coupling=SI(13.0e-12, "J/m"),
                         llg_damping=damping,
                         llg_gamma_G=SI(0.221e6, "m/A s")) 

    ksp_tols = {"DBC.rtol":1e-5*demag_tol,
                "DBC.atol":1e-5*demag_tol,
                "DBC.maxits":1000000,
                "NBC.rtol":1e-5*demag_tol,
                "NBC.atol":1e-5*demag_tol,
                "NBC.maxits":1000000,
                "PC.rtol":1e-2*pc_tol,
                "PC.atol":1e-7*pc_tol,
                "PC.maxits":1000000}
    sim = Simulation(name, ksp_tolerances=ksp_tols,
                     phi_BEM=default_hmatrix_setup)

    sim.load_mesh("disk.nmesh.h5", [("Py", mat_Py)], unit_length=1*nm)
    return sim

if not os.path.exists(relaxed_start_file):
  sim = setup_simulation("relax", 1.0)
  sim.set_H_ext(bias_H)
  sim.set_m(m0)
  sim.set_params(stopping_dm_dt=dmdt,
                 ts_rel_tol=1e-7, ts_abs_tol=1e-7)
  sim.relax()
  sim.save_data(fields='all')
  sim.save_restart_file(relaxed_start_file)
  sys.exit(0)

# Dynamics: run the dynamical simulation
sim = setup_simulation("dyn", 0.01)
sim.load_m_from_h5file(relaxed_start_file)

sim.set_H_ext(pulse, sinc_amplitude)

# Now retrieve the corresponding NumPy array
H_pulse_data = sim.get_subfield("H_ext")

# Do the same for the bias field
sim.set_H_ext(bias_H)
H_bias_data = sim.get_subfield("H_ext")

# Now the applied field at time t will be expressed as
#   H_bias_data + f(t)*H_pulse_data,
# where f(t) is the time dependence of the pulse
def update_H_ext(t_su):
    ut = float(sinc_omega*(t_su*ps - sinc_t0*ps))
    t_amp = math.sin(ut)/ut if abs(ut) > 1e-10 else 1.0

    if abs(t_amp) > 1e-4:
        H_value = H_bias_data + t_amp*H_pulse_data
    else:
        H_value = map(lambda x: float(x/SI("A/m")), bias_H)

    fieldname = 'H_ext'
    sim._fields.set_subfield(None, H_value, SI("A/m"),
                             fieldname=fieldname, auto_normalise=False)
    (mwe, field) = sim._master_mwes_and_fields_by_name[fieldname]
    ocaml.lam_set_field(sim._lam, field, "v_" + fieldname)
    print "*",

sim.pre_rhs_funs.append(update_H_ext)

sim.set_params(stopping_dm_dt=0) # Never stop for convergence
sim.relax(save=[('fields', every('time', 10*ps))],
          do=[('exit', at('stage_time', 10240*ps))])
