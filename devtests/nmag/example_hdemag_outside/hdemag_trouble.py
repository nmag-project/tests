import nmag
import pyvtk
from nmag import SI

#create simulation object
sim = nmag.Simulation()

length = SI(1e-9, 'm')

# define magnetic material
Py = nmag.MagMaterial(name = 'Py',
                      Ms = SI(1e6, 'A/m'),
                      exchange_coupling = SI(13.0e-12, 'J/m'))

# load mesh
sim.load_mesh('cube.nmesh.h5',
              [('cube', Py)],
              unit_length = length)

# set initial magnetisation
sim.set_m([1,0,0])

# Save and display data in a variety of ways
sim.save_data(fields='all') # save all fields spatially resolved
                            # together with average data

# sample demag field in outer space:


p0=[16.2,5.0,-1.2]

points=[]
hdemag_vectors=[]

for n in range(-100,101):
    pos=[p0[0],p0[1]+n/100.0, p0[2]]
    H_demag = sim.probe_H_demag_siv(pos, pos_unit=length)
    points.append(pos)
    hdemag_vectors.append(H_demag)
    # print "pos =", pos, ": H_demag = ", H_demag
    print "%8.4f %f %f %f" % (n,H_demag[0],H_demag[1],H_demag[2])

