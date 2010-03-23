import sys
import nmesh
import tables
import numpy as N
#import numarray as N
#import Numeric as N

def read_mesh_from_h5(h5file, outputfilename):
    f=tables.openFile(h5file)
    
    points = f.root.mesh['points'][0].tolist()
    simplices = f.root.mesh['simplices'][0].tolist()
    simplicesregions = f.root.mesh['sregions'][0].tolist()

    mesh = nmesh.mesh_from_points_and_simplices(points,simplices,simplicesregions)

    mesh.save(outputfilename,directory='.')


def add_mesh_to_h5(h5file, mesh, meshname = "mesh"):

    pointsa,simplicesa,surfacesa,simplicesregionsa =map(N.array,[mymesh.points,mymesh.simplices,mymesh.surfaces,mymesh.simplicesregions])

    print pointsa[0:4],pointsa.shape


    #define mesh class
    class Mesh(tables.IsDescription):
        points = tables.Float64Col(shape=pointsa.shape)
        sregions = tables.Int32Col(shape=simplicesregionsa.shape)
        simplices = tables.Int32Col(shape=simplicesa.shape)
        #surfaces = tables.Int32Col(shape=surfacesa.shape)
        name   = tables.StringCol(len(meshname)+1)
                
    # Create one table on it
    table = h5file.createTable("/", 'mesh', Mesh, "positions")

    mesh = table.row
    #add data
    mesh['name']  = 'my mesh'
    mesh['points'] = pointsa
    mesh['simplices'] = simplicesa
    #mesh['surfaces'] = surfacesa
    mesh['sregions'] = simplicesregionsa
    mesh.append()



if __name__ == "__main__":

    filename = sys.argv[1]
    h5filename = filename+'.h5nmesh'
    
    mymesh = nmesh.load(filename)
    h5file = tables.openFile(h5filename, mode = "w", title = "mesh in hdf5")
    add_mesh_to_h5(h5file, mymesh,meshname=filename)
    h5file.close()

    f=tables.openFile(h5filename)
    print f.root.mesh['simplices'][0][0:5]
    print 'done simplices'
    print f.root.mesh['points'][0][0:5]
    print 'done points'
    print N.array(mymesh.surfaces).shape
    print f.root.mesh['sregions'][0][0:5]

    read_mesh_from_h5(h5filename,filename+'.h5.nmesh')
