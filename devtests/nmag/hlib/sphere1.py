import nmag
from nmag import SI
import time
from time import sleep

ocaml.init_hlib("/home/aknittel/HLib-1.3/Library/.libs/libhmatrix-1.3.so")


#create simulation object
hp = {}
hp['algorithm']= 6
hp['nfdeg'] = 3
hp['nmin'] = 30
hp['eta'] = 2.0
hp['eps_aca'] = 0.0001
hp['eps'] = 0.001
hp['p'] = 4
hp['kmax'] = 500


sim = nmag.Simulation(use_hlib=True, hlib_params=hp)
#sim = nmag.Simulation(use_hlib=False) 

# define magnetic material
Py = nmag.MagMaterial(name = 'Py',
                      Ms = SI(1e6, 'A/m'),
                      exchange_coupling = SI(13.0e-12, 'J/m'))


# load mesh
sim.load_mesh('sphere1.nmesh.h5',
              [('sphere', Py)],
              unit_length = SI(1e-9, 'm'))

# set initial magnetisation
sim.set_m([1,0,0])

# set external field
sim.set_H_ext([0,0,0], SI('A/m'))

# Save and display data in a variety of ways
sim.save_data(fields='all') # save all fields spatially resolved
                            # together with average data

# sample demag field through sphere
for i in range(-10,11):
    x = i*1e-9                      #position in metres
    H_demag = sim.probe_subfield_siv('H_demag', [x,0,0])
    print "x =", x, ": H_demag = ", H_demag

