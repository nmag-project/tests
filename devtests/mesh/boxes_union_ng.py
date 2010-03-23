# run with ./pyfem boxes_union_ng.py 
from mesh import *

# define mesher parameters and outer box
m = mesh(frequency = 100, rod_length = 0.7, bbox = [[-2.0,-2.0,-2.0],[2.0,2.0,2.0]])

# create a first box
box1 = box(coords=[[0.0,0.0,0.0],[1.0,1.0,1.0]],shifting=[-0.5,-0.5,-0.5])

# create a secod box
box2 = box(coords=[[0.0,0.0,0.0],[1.0,1.0,1.0]],shifting=[-0.0,-0.0,-0.0])

# unite them
box3 = box1.unite(box2)

# mesh the union 
m.mesh_it([box3],visual= True,save=["box_example_ng.ps","/tmp/box_example_ng.vtk"])
