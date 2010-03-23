import time
import nmag
from nmag import SI,mesh
import os
import nfem

M_SAT=0.86e6

setupstart = time.time()

H_x = SI(0.0e6, "A/m")
H_y = SI(0.0e6, "A/m") 
H_z = SI(0.0e6, "A/m") 

intensive_param_by_name={"H_x":H_x, "H_y":H_y, "H_z":H_z}

mat_Py = nmag.MagMaterial(name="Py",
                          Ms=SI(M_SAT,"A/m"),
                          exchange_coupling=SI(13.0e-12, "J/m"),
                          llg_gamma=SI(0.2211e6, "m/(A*s)"),
                          )

sim = nmag.Simulation("bar",mesh_unit_length=SI(1e-9,"m"),
                      do_demag=True, fem_only=True)

sim.load_mesh("../../../examples/bar-with-bbox.nmesh.h5",
              [("Py", mat_Py),("void",[])])

print "*** SAVING MESH ***"
sim.save_mesh("/tmp/debug.mesh")

def initial_magnetization((x, y, z), mag_type):
    import math
    angle_deg = 45
    angle_rad = (angle_deg/360.0)*2*math.pi
    return [math.cos(angle_rad), 0, math.sin(angle_rad)]

sim.set_magnetization(initial_magnetization)

#dt = SI(5e-12, "s")
dt = SI(5e-12, "s") 
#final = SI(0.3e-9,"s")

target_time = sim.advance_time(intensive_param_by_name, 1e-6*dt)

#sim.save_field('m','barmini_restartfield.nvf')

sim.save_data_table()

#sim.save_fields_vtk('barmini_vtk%04d.vtk' % 0)

nfem.field_print_contents(sim.fields["m"])

calcstart = time.time()

for i in range(1, 61):
    time_ = dt*i
    print "Time spent so far %g" % (time.time()-calcstart)
    target_time = sim.advance_time(intensive_param_by_name, time_)

    sim.save_fields(fieldnames=sim.fields.keys())
    #sim.save_fields()

    #sim.save_field('m',filename='barmini_restartfield.nvf')

    #write SI data into default file

    #Matteo: the next line is slow 
    sim.save_data_table()
    sim.save_fields_vtk('fem_vtk%04d.vtk' % i)

calcstop = time.time()

print "Setup took %g seconds" % (calcstart-setupstart)
print "Time loop took %g seconds" % (calcstop-calcstart)
print "Total time: %g seconds" % (calcstop - setupstart)
#sim.save_fields_vtk('barmini_vktfinal.vtk')



