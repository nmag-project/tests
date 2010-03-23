import nmag
from nmag import SI
import sys
import time
from time import sleep

filename=sys.argv[1]
ms=float(sys.argv[2])            #retrieving of the saturation magnetisation
exchange=float(sys.argv[3])       #the exchange constant

    
sim = nmag.Simulation(use_hlib=False, use_pvode=False)


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
