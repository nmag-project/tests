import time, math,os,sys
import nmag
from nmag import SI,mesh

# DDD Note: we also have to define an anisotropy for this to work!


meshfile = "./bar60_60_100_ordered.nmesh.h5"

mat_Py = nmag.MagMaterial(name="Py",
                          Ms=SI(1e6,"A/m"),
                          exchange_coupling=SI(13.0e-12, "J/m"))

sim = nmag.Simulation()
                      

sim.load_mesh(meshfile, [("Py", mat_Py)],unit_length=SI(1e-9,"m"),distrib=distrib)


angle_deg = 45
angle_rad = angle_deg/360.*2*math.pi
sim.set_m([math.cos(angle_rad), 0, math.sin(angle_rad)])

sim.set_params(ts_rel_tol=2.7e-05 , ts_abs_tol=2.7e-05)

probed=sim.probe_subfield_siv('m_Py',[5e-9,5e-9,5e-9])
print "### M at T=T0: ",probed



for i in range(1,51):

    tn = SI(i*10e-12,"s")
    print "starting loop, i=%d, target time=%s" % (i,tn)
    print "T=",tn
    target_time = sim.advance_time(tn)
    if i % 5 == 0:
        sim.save_data(fields='all')
    else:
        sim.save_data()

probed=sim.probe_subfield_siv('m_Py',[5e-9,5e-9,5e-9])
print "### M at T=T_final: ",probed

