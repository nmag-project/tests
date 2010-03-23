############### create an antidot array of 16 holes
import mesh
import Numeric
pi = Numeric.pi

#define a new mesher
mesher = mesh.mesher()
mesher.set_topology_threshold(0.1)
driver = mesh.driver()
driver.step(200)

# first hole in the left bottom corner
hole1 = mesh.ellipsoid(length=[1.0,1.0],shifting=[-3.0,-3.0],outer_box=[[-5.0,-5.0],[5.0,5.0]])

# second hole on the right of hole1
hole2= hole1.copy()
hole2.shift([2.0,0.0])

# copy the previous couple of holes on the right
couple_holes = hole1+hole2
copy_couple_holes= couple_holes.copy()
copy_couple_holes.shift([0.0,2.0])

# create a compound of 16 holes
compound = couple_holes+copy_couple_holes

# mesh the compound with the user defined mesher and driver
# visualising the mesh generation. Save the final (+intermediate)
# mesh in files 
compound.mesh_it(visual=True,rod_length= 0.3, mesher=mesher, save=["holes.ps","/tmp/holes.vtk"],driver=driver)
