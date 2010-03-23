# run with ./pyfem test_python_interface.py
import mesh
import Numeric
pi = Numeric.pi

############# create a square ring from individual sections 
# create bottom section
bottom = mesh.box(coords=[[0.0,0.0],[6.0,1.0]],outer_box=[[-5.0,-5.0],[5.0,5.0]],shifting=[-3.0,-3.0])

# create rigth section
right = bottom.copy()
right.rotate(1,0,pi/2.,bc = False)

# create top section
top = right.copy()
top.rotate(1,0,pi/2.,bc = False)

# create left section
left = top.copy()
left.rotate(1,0,pi/2.,bc=False)

# mesh them one by one (independently)
# and save mesh in a file
ring = bottom+right+top+left
ring.mesh_it(save=["simple_rotation.ps","simple_rotation.dat"])
print "Finished simple rotation"
raw_input()

#----------------------------------------------------

############## create a square ring from the union of sections
def driver_do(nr_piece,n,mesh):
    """Function to be executed
    every n steps 
    """
    print "Object nr. %d, iteration nr. %d" %(nr_piece, n)


# define a new driver (instead of using the default one)
driver = mesh.driver()
driver.fun(driver_do)
driver.step(200)

# create a compound of three sections 
rtl = right+top+left

# mesh them all together (one shot)
ring2 = bottom.unite(rtl)

# save the mesh in a postsript and "pyfem" file
ring2.mesh_it(save=["union.ps","union.dat"])
print "Finished union"
raw_input()
#------------------------------------------------------

############### create an antidot array of 16 holes

#define a new mesher
mesher = mesh.mesher()
mesher.set_topology_threshold(0.1)
driver = mesh.driver()
driver.step(100)

# first hole in the left bottom corner
hole1 = mesh.ellipsoid(length=[1.0,1.0],shifting=[-3.0,-3.0],outer_box=[[-5.0,-5.0],[5.0,5.0]])

# second hole on the right of hole1
hole2= hole1.copy()
hole2.shift([2.0,0.0])

# copy the previous couple of holes on the right
couple_holes = hole1+hole2
copy_couple_holes= couple_holes.copy()
copy_couple_holes.shift([4.0,0.0])

# create the bottom line of holes
bottom_holes = couple_holes+copy_couple_holes

# create the second line
second_line = bottom_holes.copy()
second_line.shift([0.0,2.0])

# create the couple of lines
two_lines = bottom_holes+second_line

# copy the couple of lines on their top
copy_two_lines = two_lines.copy()
copy_two_lines.shift([0.0,4.0])

# create a compound of 16 holes
compound = two_lines+copy_two_lines

# mesh the compound with the user defined mesher and driver
# visualising the mesh generation. Save the final (+intermediate)
# mesh in files 
compound.mesh_it(visual=True,rod_length= 0.3, mesher=mesher, save=["holes.ps","/tmp/holes.vtk"],driver=driver)
