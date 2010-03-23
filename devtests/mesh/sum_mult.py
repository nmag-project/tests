# run with ./pyfem test_python_interface.py
import mesh
driver = mesh.driver()
driver.step(100)

### create box
box = mesh.box(coords=[[0.0,0.0],[2.0,1.0]],outer_box=[[-5.0,-5.0],[5.0,5.0]],shifting=[-3.0,-3.0])

box2 = box+[2.0,0.0]         # shifts the box
box4 = box+box2              # create a new object which is a sum of objects
box4.set_shift([0.0,1.5])    # set shift to use in multiplication (repetition)
box3 = box4*3                # repeat the box4 three times
# mesh in files 
box3.mesh_it(visual=True, driver=driver,save=["holes.ps","/tmp/holes.vtk"])
