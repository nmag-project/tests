import nmag
from nmag import SI, mesh
import specification
import sets
import nfem as nfem
import os, sys, math
from nsim.si_units.si import degrees_per_ns
from nsim import sets

def mumag2_simulation(mesh_file, mesh_unit, Hs, m0):
    mat_Py = nmag.MagMaterial(name="Py",
                              Ms=specification.m_sat,
                              exchange_coupling=specification.exchange_coupling,
                              llg_gamma_G=SI(0.2211e6, "m/(A*s)"),
                              llg_damping=SI(1.0),
                              llg_normalisationfactor=SI(0.01e12, "1/s")
                              )

    sim = nmag.Simulation(specification.sim_name)

    mf = "../" + mesh_file
    if os.path.exists(mf):
        sim.load_mesh(mf, [("Py", mat_Py)], unit_length=mesh_unit)
    else:
        raise StandardError,"Need file %s" % mf

    sim.set_m(m0)

    sim.set_timestepper_params(stopping_dm_dt=1.0*degrees_per_ns)
    #sim.set_timestepper_params(rel_tolerance=1e-6, abs_tolerance=1e-6)

    h_pars = []
    m_pars = []
    mxs = []
    mys = []
    ms = []
    ts = []
    def save_stuff(sim):
        t = sim.time
        H = Hs[sim.stage-1]
        print "Stage %d converged!" % sim.stage
        result = nfem.integrate_field(sim.fields["m"], "m_Py")
        volume = sim.region_volume("Py")
        m = [mi/volume for mi in result[0][1]]
        mx, my, mz = m
        h_proj = sets.projection(axis=H_direction, vector=H)
        h_par = float(h_proj/specification.m_sat)
        m_par = sets.projection(axis=H_direction, vector=m)
        h_pars.append(h_par)
        m_pars.append(m_par)
        mxs.append(mx)
        mys.append(my)
        ms.append(m)
        ts.append(t.value)

    from nsim.when import every, at
    stp = specification.save_averages_every_step
    stg = specification.save_averages_every_stage
    when_save_averages = at('convergence')
    if stg: when_save_averages = when_save_averages & every(int(stg), 'stage')
    if stp: when_save_averages = when_save_averages | every(int(stp), 'step')
    sim.hysteresis(Hs, save=[(save_stuff, at('convergence')),
                             ('averages', when_save_averages)])

    hc = min(sets.intersections(0.0, zip(h_pars, m_pars)))
    mrx = min(sets.intersections(0.0, zip(mxs, h_pars)))
    mry = min(sets.intersections(0.0, zip(mys, h_pars)))

    results = {"h_pars":h_pars, "m_pars":m_pars, "mxs":mxs, "mys":mys,
               "ms":ms, "hc":hc, "mrx":mrx, "mry":mry, "ts":ts}
    return results

#-----------------------------------------------------------------------------

# The list of values taken by the norm of the applied field
H_norms = [0.6, 0.4,
          0.2, 0.16, "...",
          0, -0.005, "...",
          -0.045, -0.0455, "...", # should contain Hc: we map it better!
          -0.058] #, -0.065, "...", -0.2]

h0 = specification.Hext_initial/specification.m_sat
h1 = specification.Hext_final/specification.m_sat
H_norms = [h0, [specification.num_stages], h1]

#H_norms = [0.6, 0.594186, "...", -0.2] # For now we stick at what we do with magpar

# The direction of the applied field
H_direction = specification.vHext_direction

# From the norms and the direction (which is constant) we derive
# all the values that the applied field will take during the simulation
# Note we express all in terms of the saturation magnetisation.
Hs = sets.vector_set(direction=H_direction, norm_list=H_norms,
                     units=specification.m_sat)

# Initial magnetisation
def m0((x, y, z), mag_type):
    import math
    x = 1.0/math.sqrt(3)
    return [x, x, x]

def out(line, header=False, file="nmag.dat"):
    import os
    if header and os.path.exists(file): return
    f = open(file, "a")
    f.write(line)
    f.close()

out("# d/l_ex  Hc/Ms  Mr_x/Ms  Mr_y/Ms\n", header=True)

args = []
if len(sys.argv) > 1:
    # We take only arguments which do not contain '-'
    # (just to avoid considering '-ldebug' and other options)
    for arg in sys.argv[1:]:
        if not('-' in arg): args.append(arg)

if len(args) != 0:
    d_list = sets.float_set(args)
else:
    d_list = sets.float_set([5]) #, 6, "...", 10])

for d in d_list:
    mesh_file = specification.bar_mesh
    r = mumag2_simulation(mesh_file, specification.mesh_unit_length, Hs, m0)
    #ocaml.sys_check_heap()

    mesh_unit_length_nm = float(specification.mesh_unit_length/SI(1e-9, "m"))
    out("# d=%f, mesh='%s', scaling=%f\n" % (d, mesh_file, mesh_unit_length_nm))
    out("%f %f %f %f\n" % (d, r["hc"], r["mrx"], r["mry"]))

    m_out = open("m_d%03.0f.dat" % d, "w")
    for h_par, m_par, (mx, my, mz), t in zip(r["h_pars"], r["m_pars"], r["ms"], r["ts"]):
        m_out.write("%g %g %g %g %g %g\n" % (h_par, m_par, mx, my, mz, t))
    m_out.close()

#import time
#calcstop = time.time()
#calcstart = time.time()
#setupstart = time.time()
#print "Setup took %g seconds" % (calcstart-setupstart)
#print "Time loop took %g seconds" % (calcstop-calcstart)
#print "Total time: %g seconds" % (calcstop - setupstart)
#sim.save_fields_vtk('vktfinal.vtk')
