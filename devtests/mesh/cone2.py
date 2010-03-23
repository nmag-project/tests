###########################################################
# example to show how to use mayavi to visualize our mesh #
###########################################################
#
# Usage: load pyfem and execute
#        >> execfile("open_vtk_in_mayavi.py") 
#
# We need the pylab module to open mayavi (it seems that
# mayavi module is not sufficient.
# To show it comment out only the line
#
#        #import pylab
#
# and reload pyfem.
#
# The open_vtk_data function doesn't work on our structure
# pyvtk.VtkData( pyvtk.UnstructuredGrid(points, triangle) ).
# To show it comment out only the lines
#
#        v.tofile('/tmp/show_2d.vtk')
#        vd=myv.open_vtk('/tmp/show_2d.vtk',config=1)
#
# in driver_do(nr_piece, n,mesh).
# (the error should be
#        AttributeError: 'NoneType' object has no attribute 'mapper'
# )
# The solution is to use a file to write on and read from
# our mesh structure. To show it comment out only the line
#
#        vd = myv.open_vtk_data(v)
#
# in driver_do(nr_piece, n,mesh).

from __future__ import division
import Numeric
import vtk
# import mayavi
import pyvtk
# import pylab
import numarray
import sys

global qual_mesh
qual_mesh = 0


def in2circ(ccradii, icradii, mode=2):
    """This function calculates a number representative of a triangles
       regularity. The ratio of inradius / circumradius. The ratio is
       multiplied by a factor of 2 for 2D meshes and 3 for 3D meshes.
       Hence the value will be unity for an equilateral triangle or regular
       tetrahedron.

       Author: James Kenny              Last modified: 4/12/05
       Filename: meshviz2.py

       Input: list of circumradii (ordered same as cells)
              list of inradii
              mode (2 -> 2d, 3 -> 3d), default = 2d

       Output: array ready for use as cell_data
    """
    import Numeric

    # initialise an appropriately sized array
    if len(ccradii) != len(icradii):
        raise ValueError, "Lists not of equal length."
    else:
        in2circ = Numeric.zeros([len(ccradii)],Numeric.Float32)

    # populate in2circ array with the required values
    for i in range(len(ccradii)):
        in2circ[i] = (mode*icradii[i])/ccradii[i]

    global qual_mesh
    qual_mesh = Numeric.add.reduce(in2circ)/len(in2circ)
    qual_tmp = numarray.array(in2circ[:])
    print "--------------------------------------> ", qual_mesh, qual_tmp.min()
    return in2circ

def mesh2vtk(mesh):
    """This function converts the appropriate data from the mesh info arrays
       output from the mesher, into vtkUnstructuredGrids ready for
       visualisation in MayaVi. Uses PyVTK.

       Automatically chooses between 2D and 3D meshes. 1D may be covered later.

       Can ask for in2circ data to be calculated.

    """
    import tempfile, os, vtkpython

    reader = vtkpython.vtkUnstructuredGridReader()

    # decide if this is a 2D or 3D mesh
    dim = len(mesh[0][2][0])
    if dim == 0 or dim > 3:
        raise ValueError, "Mesh should be 2D or 3D." 
    else:
        print "Dimension of the space is %d" % (dim)


    # load points and bodies and initialize lists for other variables
    points = mesh[0][2]
    bodies = mesh[3][2]
    triangles = []
    tetra = []
    ccradii = []
    icradii = []
    
    # 2D case
    if dim == 2:

        # read appropriate parts of the mesh ready for PyVTK
        for i in mesh[2][2]:
            triangles.append(i[0])
            ccradii.append(i[1][1])
            icradii.append(i[2][1])

        # now create the vtkUnstructuredGrid using PyVTK
        # extend the 2D points with a null coordinate in the 3rd
        # direction to avoid vtk complaints
        size = len(points)
        zeros = Numeric.zeros(size)
        zeros = Numeric.reshape(zeros,(zeros.shape[0],1))
        points = Numeric.concatenate((points,zeros), axis=1)

        # use pyvtk to convert the mesh data into a vtkUnstructuredGrid
        ug = pyvtk.UnstructuredGrid(points, triangle=triangles)
        data = pyvtk.VtkData(ug)
        in2circData = in2circ(ccradii, icradii)
        data.cell_data.append(pyvtk.Scalars(in2circData, "in2circ"))

    # 3D case
    elif dim == 3:
        # read appropriate parts of the mesh ready for PyVTK
        points = mesh[0][2]
        bodies = mesh[3][2]
        tetra = []
        ccradii = []
        icradii = []

        # read appropriate parts of the mesh ready for PyVTK
        for i in mesh[2][2]:
            tetra.append(i[0])
            ccradii.append(i[1][1])
            icradii.append(i[2][1])

        # use pyvtk to convert the mesh data into a vtkUnstructuredGrid
        ug = pyvtk.UnstructuredGrid(points, tetra=tetra)
        data = pyvtk.VtkData(ug)
        in2circData = in2circ(ccradii, icradii)
        data.cell_data.append(pyvtk.Scalars(in2circData, "in2circ"))

    # workaround to avoid writing to files on disk all the time
    # write to a fake temporary file and read from there
    # vtk-python data structures are not identical in memory!
    file_name = tempfile.mktemp(suffix='.vtk')
    data.tofile(file_name, format='ascii')
    reader.SetFileName(file_name)
    reader.Update()
    os.remove(file_name)

    return reader.GetOutput()


def main():


#    global myv
#    myv = mayavi.mayavi()   # open mayavi outside of loop

    def driver_do(nr_piece, n,mesh):

        print "Iteration: %d" %(n)
        mesh_info = ocaml.mesh_plotinfo(mesh)
#        myv.close_all()
#        v = mesh2vtk(mesh_info)
#        vd = myv.open_vtk_data(v)
#        dvm = myv.get_current_dvm()
#        mm = dvm.get_current_module_mgr()
##        mm.scalar_lut_h.load_lut_from_file("gauss.lut")
##        mm.scalar_lut_h.range_on_var.set(1)
##        mm.scalar_lut_h.range_var.set((0, 1))
##        mm.scalar_lut_h.set_range_var()
#        md = myv.load_module('SurfaceMap',0)
#        myv.renwin.z_plus_view()
#        vd2 = myv.open_vtk_data(v)
#        dvm = myv.get_current_dvm()
#        mm = dvm.get_current_module_mgr()
##        mm.scalar_lut_h.load_lut_from_file("gauss.lut")
##        mm.scalar_lut_h.range_on_var.set(1)
##        mm.scalar_lut_h.range_var.set((0, 1))
##        mm.scalar_lut_h.set_range_var()
#        md2 = myv.load_module('SurfaceMap',0)
#        md2.mapper.ScalarVisibilityOff()
#        md2.actor.GetProperty().SetRepresentationToWireframe()
#        myv.renwin.z_plus_view()
#        myv.Render()
#        raw_input()

    rod_length=0.6
    my_mdefaults=ocaml.mesher_defaults
    my_gendriver=ocaml.make_mg_gendriver(120,driver_do)

    # create a mesh
    # the cone is called with arguments in the order:
    # center1, radius1, center2, radius2
    frustum = ocaml.body_box([0.0,0.0,-6.0],[0.1,1.0,6.0])
    density="""
    {
    density=1.0;
    }
    """

    mesh = ocaml.mesh_bodies_raw(my_gendriver,my_mdefaults, [-6.0,-6.0,-6.0], [6.0,6.0,6.0], 1,[frustum], rod_length,density)
    mesh_info = ocaml.mesh_plotinfo(mesh)
    v = mesh2vtk(mesh_info)

if __name__ == "__main__":
    main()

