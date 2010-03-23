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

xyzrange=[(-10,21,1),(-10,21,1),(-4,5,1)]


points=[]
hdemag_vectors=[]

for xc in range(xyzrange[0][0],xyzrange[0][1]):
    for yc in range(xyzrange[1][0],xyzrange[1][1]):
        for zc in range(xyzrange[2][0],xyzrange[2][1]):
            pos=[xc,yc,zc]
            H_demag = sim.probe_H_demag_siv(pos, pos_unit=length)
            points.append(pos)
            hdemag_vectors.append(H_demag)
            print "pos =", pos, ": H_demag = ", H_demag

vtk = pyvtk.VtkData(pyvtk.UnstructuredGrid(points),
                    pyvtk.PointData(pyvtk.Vectors(hdemag_vectors)),
                    'H_demag field')

vtk.tofile('h_demag')
