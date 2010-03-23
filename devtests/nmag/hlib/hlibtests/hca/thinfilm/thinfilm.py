import nmag
from nmag import SI
import sys
import time
from time import sleep

ocaml.init_hlib("/home/aknittel/HLib-1.3/Library/.libs/libhmatrix-1.3.so")

#the length has to be 9 or 10, depending on whether one uses the option --clean
assert (len(sys.argv)==9 or len(sys.argv)==10), "The number of command line parameters is not 9 or 10."

filename=sys.argv[1]
ms=float(sys.argv[2])            #retrieving of the saturation magnetisation
exchange=float(sys.argv[3])       #the exchange constant

#create simulation object
hp = {}
hp['nfdeg'] = int(sys.argv[4])
hp['nmin'] = int(sys.argv[5])
hp['p'] = int(sys.argv[6])
hp['eta'] = float(sys.argv[7])
hp['eps'] = float(sys.argv[8])

sim = nmag.Simulation(use_hlib=True, use_pvode=False, hlib_params=hp)

# define magnetic material
Py = nmag.MagMaterial(name = 'Py',
                      Ms = SI(ms, 'A/m'),
                      exchange_coupling = SI(exchange, 'J/m'))

# load mesh
sim.load_mesh(filename,
              [('thinfilm', Py)],
              unit_length = SI(1e-9, 'm'))

# set initial magnetisation
sim.set_m([0,0,1])

# set external field
sim.set_H_ext([0,0,0], SI('A/m'))

# Save and display data in a variety of ways
sim.save_data(fields='all') # save all fields spatially resolved
                            # together with average data
