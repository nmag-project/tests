# run with ./pyfem fixed_points_2d.py 
from mesh import *

# define mesher parameters and outer box
m = mesh(frequency = 1000, rod_length = 0.5, bbox = [[-4.0,-4.0],[4.0,4.0]])


m.fixed_points = [[0.,0.],[-0.5,0.],[-0.5,0.5],[0.,0.5]] 
box1 = box(coords=[[0.0,0.0],[1.0,2.0]])

a = m.mesh_it([box1],visual=False, save=["fixed_points.ps"])

