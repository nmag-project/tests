# run with ./pyfem boxes_union_ng.py 
from mesh import *

# define mesher parameters and outer box
m = mesh(frequency = 1000, rod_length = 0.4, bbox = [[-2.0,-2.0],[2.0,2.0]])

# create a first box
box1 = box(coords=[[0.0,0.0],[1.0,1.0]],shifting=[-0.0,-0.0])
box1.rotate(z=45)
box1.shift([-0.5,0.5])

#create a second box
box2 = box(coords=[[0.0,-1.0],[0.5,0.0]],shifting=[0.5,-0.5])
#Giuliano, if you add the second box here and below in mesh_it, it seems we lose
#the first box.
#
#Any idea why?

# unite them
#box3 = box1.unite(box2)

# mesh the union 
m.mesh_it([box1,box2],visual= False,save=["box_example_2d.ps","box_example_2d.vtk"])
