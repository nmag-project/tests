import time
import nmag
from nmag import SI,mesh
import os

M_SAT=0.86e6

time_total = -time.time()
time_writing = 0.0
time_initialising = -time.time()
mat_Py = nmag.MagMaterial(name="Py",
                          Ms=SI(M_SAT,"A/m"),
                          exchange_coupling=SI(13.0e-12, "J/m"),
                          llg_gamma_G=SI(0.2211e6, "m/A s"),
                          # llg_damping=SI(0,"")
                          )


sim = nmag.Simulation()

meshfile = "../bar30_30_100.nmesh.h5"

sim.load_mesh(meshfile, [("Py", mat_Py)],unit_length=SI(1e-9,"m"))

import math
angle_deg = 45
angle_rad = angle_deg/360.*2*math.pi
sim.set_m([math.cos(angle_rad), 0, math.sin(angle_rad)])
sim.set_params(ts_rel_tol=2.7e-05 , ts_abs_tol=2.7e-05)

dt = SI(5e-12, "s") 

time_initialising += time.time()
time_loop = -time.time()

for i in range(0, 60):
    time_ = dt*i
    print "Time spent so far %g" % (time_total+time.time())
    target_time = sim.advance_time(time_)

    time_writing -= time.time()
    if i % 5 == 0:
        sim.save_data(fields='all') #write spatial averages plus spatially resolved fields
    else:
        sim.save_data() #write only spatial averages 
    time_writing += time.time()

time_loop += time.time()

time_total += time.time()
time_simulating = time_loop - time_writing
print "Setup took %g seconds" % time_initialising
print "Simulation loop took %g seconds" % time_loop
print "Writing data took: %g seconds" % time_writing
print "Timestepper took: %g seconds" % time_simulating
print "Total time: %g seconds" % time_total


def print_sorted_dictionary( timing, title=None, total_time=True ):

    def sorthelper(x,y):
        if x[1] < y[1]:
            return 1
        elif x[1] == y[1]:
            return 0
        else:
            return -1
    
    tmp1 = []
    total_time
    for key,value in timing.items():
        tmp1.append((key,value))
        total_time += value

    tmp1.sort(sorthelper)


    if title:
        print title

    for name,time in tmp1:
        print "%50s : %s" % (name,time)

    if total_time:
        print "Sum of recorded time :", total_time

    return tmp1, total_time
    

print_sorted_dictionary( nmag.timing, title="nmag.timing")


import nfem.hdf5_v01
from nfem.hdf5_v01 import append_fields_timings


print_sorted_dictionary( append_fields_timings, title="nfem.hdf5_v01.append_fields_timing")


from nfem.hdf5_v01 import append_averages_timings

print_sorted_dictionary( append_averages_timings, title="nfem.hdf5_v01.append_averages_timing")


    
    


"""#
The content of nmag.timing are
                        compute_averages_maxangles : 18.2311873436
                              save_data_hd5hasstep : 0.00609111785889
                                       save_fields : 7.57376790047
                                         save_data : 49.9633116722
     compute_averages_average_of_material_integral : 0.0245378017426
                                  compute_averages : 27.3043751717
                               fun_update_energies : 0.0
                                     append_fields : 7.55830693245
                  compute_averages_integrate_field : 8.71562051773


(fangohr 26/11/2007 21:50): the above data is from a run on AMD Athlon(tm) XP 2600+ machine.

The thing I'd like to improve first is the time that is spent in
compute_averages_maxangles. The relevant call to ocaml is this line::

   dofname_maxangle_list = ocaml.mumag_vector_field_max_angles(self._fields["m"])

in interface/nmag4/main.py in function _compute_averages( self ).

Looking at the timing data above, we spend 18.2 seconds in this
function for 60 calls. That's about a third of a second per call.

More importantly: the total time in compute_averages is 27 seconds, of which 8.7 seconds are spent to work out the averages (actually: integrals that are then divided by the volume) of actual fields. While it would be good to make this faster, it is already pretty fast considering that we have many fields (order of magnitude is 10) that are averaged during this time. Once we take the 8.7 seconds away from 27 seconds, the major part of the time is taken by the computation of the max angles.

The max angle computation function has to 

- go through mesh and

- find neighbouring nodes that carry the same type of magnetisation
  (i.e. the same subfields of the field 'm'; typically (and in the above
  example) we have only one such subfield which here is m_Py)

- for all neighbouring pairs work out the angle alpha between the magnetisation
  vectors m1 and m2 (for example using <m1,m2> = |m1| |m2| cos(alpha).) Let's not
  rely on |m1| and |m2| being of unit 1.0 yet --- this may not be the case in some
  thermal (LLB) simulations.

- return the largest of these angles (in degree or radian, at the very end we need degree
  for the micromagnetic user but we can convert at Python level).

The function is currently fairly slow (this is based on my gut feeling
of how long this process should take but I am fairly confident here).

What is less clear is why it is so slow. From what I remember when I
looked at this a long time ago, we work out the relevant nearest
neighbours every time we call the function. What we should do instead,
is to create this meta information with the first call, and store it
somewhere in the ocaml workings. Then, with the next n calls, we just
work through the stored list of nearest neighbours and compute the
angles alpha. This should be faster.


The same data as shown above but obtained on eta (far more useful):

With 4566 (before any improvements have started).

stepper took: 141.017 seconds
Total time: 237.341 seconds
The content of nmag.timing are
                        compute_averages_maxangles : 11.3246648312
                              save_data_hd5hasstep : 0.00756597518921
                                       save_fields : 5.03114652634
                                         save_data : 25.9705519676
     compute_averages_average_of_material_integral : 0.019953250885
                                  compute_averages : 16.9217891693
                               fun_update_energies : 0.0
                                     append_fields : 5.02354121208
                  compute_averages_integrate_field : 5.32713961601


With Giuliano's initial improvements (4808):


The content of nmag.timing are
                        compute_averages_maxangles : 7.00711345673
                              save_data_hd5hasstep : 0.00509548187256
                                       save_fields : 5.53281021118
                                         save_data : 28.6399300098
     compute_averages_average_of_material_integral : 0.019565820694
                                  compute_averages : 12.4877052307
                               fun_update_energies : 0.0
                                     append_fields : 5.52540802956
                  compute_averages_integrate_field : 5.21418166161






After revision 4815 (new data structure in mwe, we now compute all the
links between neighbouring subfield sites only once, and reuse this),
we get the following timings:

                        compute_averages_maxangles : 0.651549339294
                              save_data_hd5hasstep : 0.00505185127258
                                       save_fields : 5.43155503273
                                         save_data : 22.5681452751
     compute_averages_average_of_material_integral : 0.0193021297455
                                  compute_averages : 6.3275604248
                               fun_update_energies : 0.0
                                     append_fields : 5.41513705254
                  compute_averages_integrate_field : 5.40512657166


This means that we are -- in comparison to the orginal version -- 17
times faster.

The time it takes to call compute_averages_maxangles once is
0.19. THis means that we have made subsequent calls faster by a factor
of 11.3/(0.65-0.19)=24.5

"""




# create_field_table : 5.25041389465 (saving 60 times field data)
