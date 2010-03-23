""" Mesh class. The purpose of this module is to have
    an interface which hides all the OCaml calls to the
    mesh generator. 
    
    Author: Giuliano Bordignon
    Last modified: 09/03/06
"""
from __future__ import division
import mesh
import ocaml
print dir(ocaml)

class driver:
    def __init__(self, fun= [], every_nr_steps = 1000):
        """driver( f:f(nr_piece,iteration_nr,mesh), nr_steps: int).
        Create a driver which executes the function f every nr_steps.
        The arguments of the function are
        
        * nr_piece = index of the meshing object
        * iteration_nr = number of iteration in the relaxation process
        * mesh = mesh class

        """
        if fun == []:
            self.driver_do= self._default_fun
        else:
             self.driver_do = fun
            
        self.every_nr_steps = every_nr_steps

    def step(self,new_nr_steps = 0):
        """step( new_nr_step:int ).

        Function to change the number
        of steps for the execution of the function f
        """
        self.every_nr_steps = new_nr_steps

    def fun(self,new_fun):
        """fun( new_fun:f(nr_piece,iteration_nr,mesh) ). Change the function
        to be executed every nr_steps
        """
        self.driver_do = new_fun
    
    def _default_fun(self,nr_piece,n,mesh):
        """Default function for the driver
        """
        pass

class mesher:
    """Class to create the mesher to be used in the mesh algorithm.
    """
    def __init__(self):
        """mesher().

        Function to create a mesher
        """
        self.copy()
    
    def copy(self):
        """copy().

        Function to create a copy of the 
        mesher. The parameters of this mesher can be
        modified.        
        """
        self.my_mesher = ocaml.copy_mesher_defaults(ocaml.mesher_defaults)

    def set_max_relaxation(self,scale = 3.0):
        """set_scaling_movement( scale:float ).

        Function to change
        the behaviour of the mesh algorithm at the beginning of the
        mesh generation. It increases the max displacement before a
        re-triangulation, the time_step and the topology threshold
        """
        self.scaling_movement = scale
        ocaml.mesher_defaults_set_tolerated_rel_movement(self.my_mesher,self.scaling_movement)
        
    def set_topology_threshold(self,thresh = 0.2):
        """set_topology_threshold( thresh:float ).

        Function to change
        the default value of the topology threshold. The mesher
        re-triangulates if the movement of one of the points exceeds
        this value.
        """
        
        self.topology_threshold = thresh
        ocaml.mesher_defaults_set_topology_threshold(self.my_mesher,self.topology_threshold)
        
    def set_time_step_scale(self,scale = 0.05):
        """set_time_step( scale:float ).

        Function to change
        the default value of the scaling factor for the time
        step. Using the expression

               dT = (p_(n+1) - p_(n))/F

        with
        
        * p_(n) = position of the node at n-th iteration
        * F = force acting on that node

        the time step is scale*max(dT)
        """

        self.scaling_time_step = scale
        ocaml.mesher_defaults_set_time_step_scale(self.my_mesher,self.scaling_time_step)
        
    def set_tolerated_rel_move(self,scale = 0.004):
        """set_tolerated_rel_move( scale:float ).

        Function to change
        the default value of the tolerated relative movement.
        The mesher stops when the relative movement of all the points
        is within this value. 
        """
        
        self.scaling_tolerated_move = scale
        ocaml.mesher_defaults_set_tolerated_rel_movement(self.my_mesher, self.scaling_tolerated_move)

class mesh_obj:
    def __init__(self):
        """Base class of a mesh object
        """
        self.obj = []
        self.bbox = [[],[]]
        self.rod_length = 0.5

    def _default_fun(self,nr_piece,n,mesh):
        """Default function for the driver
        """
        pass

    def mesh_it(self, rod_length = 0.5 , driver = [],mesher = [], bbox = [], density = "", visual = False, angles = False, save = []):
        """mesh_it(rod_length:float, driver, mesher, \
        bbox:[float list,float list]), density, visual:bool,
        save:string list).
        
        Function to mesh the present object(s). The rod_length
        is the desired length of the connections between the mesh nodes,
        a value which is weighted with the C function density. The bbox
        defines the outer boundary box of the mesh. The flag visual
        consents to visualise the mesh during its relaxation process,
        and it can be saved specifying the file (with format) in the save
        list.
        Possible formats are postscript file(s) ("ps" extension) (2D only),
        vtk file(s) ("vtk" extension) (included the ones created at every
        visualization step) and "pyfem" format ("dat" extension).
        The function returns the mesh data in a python list of lists
        (the content is clear once they are inspected).
        """
        
        self.rod = rod_length
        self.density = density
        if mesher == []:
            self.mesher = ocaml.mesher_defaults
        else:
            self.mesher = mesher.my_mesher

        self.__file_vtk = ""
        self.__file_ps = ""
        self.__file_dat = ""
        self.__file_png = ""
        globals()['fig_number']=0
        globals()['angles_time']=[]
        globals()['default_iterations'] = 200



        def check_save():
            """Function to check if the mesh has to be saved
            in any format.
            """

#            print "check_save"

            if len(save)>0:
                for filename in save:
                    if filename[-3:]=="dat":
                        self.__file_dat = filename
                    elif filename[-3:]=="vtk":
                        self.__file_vtk = filename
                    elif filename[-3:]==".ps":
                        self.__file_ps = filename
                    elif filename[-3:]=="png":
                        self.__file_png = filename
                    else:
                        ValueError ("wrong extension in save file name")

#            print self.__file_vtk, self.__file_ps, self.__file_dat, self.__file_png
            
        if visual: # Initialisation of mayavi if argument visual = True
#            print "load mayavi"
            import mayavi, pylab # Tk error without pylab
            self.myv = mayavi.mayavi()


        def check_vtk(nr_piece,n,mesh):
#            print "check_vtk -- 0"
            if visual or self.__file_vtk!="":
#                print "mesh_info"
                mesh_info = ocaml.mesh_plotinfo(mesh)
#                print "check_vtk -- 1"
                v = self._mesh2vtk(mesh_info,self.__file_vtk,"-"+str(nr_piece),"-"+str(n))
#                print "check_vtk -- 2"


                if visual:                   
#                    print "visual"
                    # Function executed for argument visual = True
                    self.myv.close_all()
                    vd = self.myv.open_vtk_data(v)
                    dvm = self.myv.get_current_dvm()
                    mm = dvm.get_current_module_mgr()
                    md = self.myv.load_module('SurfaceMap',0)

                    # reverse LUT
                    luthandler = mm.get_scalar_lut_handler()
                    luthandler.set_lut_red_blue()
                    
                    # display legend, vertically with shadow effect
                    luthandler.sc_bar.SetVisibility(1)
                    luthandler.sc_bar.GetTitleTextProperty().SetShadow(1)
                    luthandler.sc_bar.GetLabelTextProperty().SetShadow(1)
                    luthandler.sc_bar.GetPositionCoordinate().SetValue(0.01,0.15)
                    luthandler.sc_bar.SetOrientationToVertical()
                    luthandler.sc_bar.SetWidth(0.14)
                    luthandler.sc_bar.SetHeight(0.85)
#                    luthandler.sc_bar.SetTitle('in2circ')
                                  
                    self.myv.renwin.z_plus_view()
                    vd2 = self.myv.open_vtk_data(v)
                    dvm = self.myv.get_current_dvm()
                    mm = dvm.get_current_module_mgr()
                    md2 = self.myv.load_module('SurfaceMap',0)
                    md2.mapper.ScalarVisibilityOff()
                    md2.actor.GetProperty().SetRepresentationToWireframe()
                    self.myv.renwin.z_plus_view()
                    self.myv.Render()

                    # if angles analysis has been requested plot histogram in pylab now
                    if angles:
                        angles_data = self._findAngles(mesh_info)                        
                        n, bins, patches = pylab.hist(angles_data, range(0,180,5))               
                        pylab.xlabel('Internal angle in degrees')
                        pylab.ylabel('Number of occurrences')
                        pylab.title('Histogram of internal angles of %d triangles' % (len(mesh_info[2][2])))
                        pylab.axvline(x=60, color='r')                        
                        pylab.savefig(self.__file_png[:-4]+str(globals()['fig_number'])+'.png')
                        globals()['fig_number'] = globals()['fig_number'] + 1
                        pylab.show()    #(screws with Tk events)
                        pylab.clf()

                        # attempt to save time series of angles data for quality vs. time plot
                        # this temporary hack saves the median angle for the highest count bin
                        highest = 0
                        modal = 0
                        for i in range(len(n)):
                            if n[i] > highest:
                                highest = n[i]
                                modal = i
                        median = (bins[modal] + bins[modal-1])/2.
                        globals()['angles_time'].append(median)

                    raw_input('Hit Any Key to Continue')
        
        def no_driver(nr_piece,n,mesh):
            """Function executed for argument visual = False
            """
#            print "no_driver"
            check_vtk(nr_piece,n,mesh)
            pass


        def fun_from_driver(nr_piece,n,mesh):
            """Function that glues together the user-defined
            function and the (possible) visualisation of the
            mesh during relaxation process.
            """
            check_vtk(nr_piece,n,mesh)
#            print "*********************fun_from_driver"
            driver.driver_do(nr_piece,n,mesh)  #user-defined function

        check_save() # check if the mesh has to be saved

        if driver == []:   # no driver is given: use the default one
            self.driver = ocaml.make_mg_gendriver(globals()['default_iterations'], no_driver)
        else:
#            print self.__file_vtk
            self.driver = ocaml.make_mg_gendriver(driver.every_nr_steps,fun_from_driver)
            
        if bbox != []:  # overwrite bbox defined at object initialisation
            self.bbox = bbox

        
#        print self.bbox
#        print self.obj
        obj_length = len(self.obj) # number of objects to mesh

        raw_mesh = ocaml.mesh_bodies_raw(self.driver,self.mesher,\
                                         self.bbox[0],self.bbox[1],obj_length,\
                                         self.obj,rod_length,self.density)

        if self.__file_ps != "":
            ocaml.mesh2d_ps(raw_mesh,self.__file_ps,[50.0,50.0,300.0,300.0])            
        if self.__file_dat != "":
            ocaml.mesh_writefile(self.__file_dat,raw_mesh)


        # to display final results in visual mode
        if visual:
            mesh_info = ocaml.mesh_plotinfo(raw_mesh)
            v = self._mesh2vtk(mesh_info,self.__file_vtk)
            
            self.myv.close_all()
            vd = self.myv.open_vtk_data(v)
            dvm = self.myv.get_current_dvm()
            mm = dvm.get_current_module_mgr()
            md = self.myv.load_module('SurfaceMap',0)
            
            # reverse LUT
            luthandler = mm.get_scalar_lut_handler()
            luthandler.set_lut_red_blue()
            
            # display legend, vertically with shadow effect
            luthandler.sc_bar.SetVisibility(1)
            luthandler.sc_bar.GetTitleTextProperty().SetShadow(1)
            luthandler.sc_bar.GetLabelTextProperty().SetShadow(1)
            luthandler.sc_bar.GetPositionCoordinate().SetValue(0.01,0.15)
            luthandler.sc_bar.SetOrientationToVertical()
            luthandler.sc_bar.SetWidth(0.14)
            luthandler.sc_bar.SetHeight(0.85)
            # luthandler.sc_bar.SetTitle('in2circ')
            
            self.myv.renwin.z_plus_view()
            vd2 = self.myv.open_vtk_data(v)
            dvm = self.myv.get_current_dvm()
            mm = dvm.get_current_module_mgr()
            md2 = self.myv.load_module('SurfaceMap',0)
            md2.mapper.ScalarVisibilityOff()
            md2.actor.GetProperty().SetRepresentationToWireframe()
            self.myv.renwin.z_plus_view()
            self.myv.Render()

                        
            if self.__file_png:
                # if angles analysis has been requested plot histogram in pylab now
                if angles:
                    angles_data = self._findAngles(mesh_info)                        
                    n, bins, patches = pylab.hist(angles_data, range(0,180,5))
                    pylab.clf()
                    pylab.xlabel('Internal angle in degrees')
                    pylab.ylabel('Number of occurrences')
                    pylab.title('Histogram of internal angles of mesh triangles')
                    pylab.axvline(x=60, color='r')                        
                    pylab.savefig(self.__file_png[:-4]+str(globals()['fig_number'])+'.png')
                    globals()['fig_number'] = globals()['fig_number'] + 1
                    pylab.show()    #(screws with Tk events)

                    # also save time plot of angles
                    pylab.clf()
                    total_iterations = globals()['default_iterations']*len(globals()['angles_time'])
                    xvalues = range(0,total_iterations,globals()['default_iterations'])
                    pylab.plot(xvalues,globals()['angles_time'],'k+')
                    pylab.hold(True)
                    pylab.plot(xvalues,globals()['angles_time'])
                    pylab.xlabel('Number of iterations')
                    pylab.ylabel('Modal internal angle (2D) in degrees')
                    pylab.title('Plot of mesh quality against time')
                    pylab.savefig(self.__file_png[:-4]+'_time.png')

            raw_input('Hit Any Key to Exit.')
            
        else:
            mesh_info = ocaml.mesh_plotinfo(raw_mesh)
            raw_input('Hit Any Key to Exit.')
#            return self._mesh2vtk(mesh_info,self.__file_vtk,final=True)

    def shift(self, shifting = [], bc=True):
        """shift( shifting:float list, bc:bool ).

        Function to shift the
        object of the amount shifting along the axes wrt the
        centre of the body. If bc=False the shift is wrt the
        origin of coordinates system. 
        """

        if shifting == []:                           # default shift 
            for i in range(len(self.bbox[0])):
                shifting.append(0.0)

        new_obj = []                                 # create new object
        if bc:
            for obj in  self.obj:
                new_obj.append( ocaml.body_shifted_bc(obj,shifting))
        else:
            for obj in self.obj:
                new_obj.append( ocaml.body_shifted_sc(obj,shifting))

        self.obj = new_obj                           # update current object

    def set_shift(self,shifting = []):
        if shifting == []:
            for i in range(len(self.bbox[0])):
                shifting.append(0.0)
        self.shifting = shifting 

    def rotate(self, x=0.0,y=0.0,z=0.0,  bc = True):
        """rotate(x:float, y:float, z:float, bc:bool).

        Function that rotates the object of an angle corresponding
        to the value of x,y,z along this directions wrt the origin
        of the body.
        If bc=False the rotation is wrt the origin of the
        coordinate system. Bounding box is NOT updated.   
        """
        from Numeric import pi
        
        new_obj = []                                 # create new object

        dim = len(self.bbox[0])                      # rotation functions
        def x_rotation(): # only 3D
            if bc:
                return ocaml.body_rotated_bc(obj,2,1,ang)
            else:
                return ocaml.body_rotated_sc(obj,2,1,ang) 

        def y_rotation(): # only 3D
            if bc:
                return ocaml.body_rotated_bc(obj,0,2,ang)
            else:
                return ocaml.body_rotated_sc(obj,0,2,ang) 

        def z_rotation(): # 2D & 3D
            if bc:
                return ocaml.body_rotated_bc(obj,1,0,ang)
            else:
                return ocaml.body_rotated_sc(obj,1,0,ang) 

        if dim==2:                                    # append rotated object
            ang = z/180.*pi
            for obj in self.obj:
                new_obj.append(z_rotation())
        elif dim==3:
            for obj in self.obj:
                ang = x/180.*pi; x_rotation()
                ang = y/180.*pi; y_rotation()
                ang = z/180.*pi; z_rotation()
                new_obj.append(obj)

        self.obj = new_obj                           # update current object

        # bounding box is NOT updated 
 

    def scale(self, scale = []):
        """scale(scale:float list, sc:bool).

        Function that scales the object with a factor
        given by the entry of the scale list on the
        corresponding axis. Bounding box is NOT updated.
        """
        if scale == []:                              # default scale 
            for i in range(len(self.bbox[0])):
                scale.append(1.0)
                
        new_obj = []                                 # create new object
        for obj in  self.obj:
            new_obj.append(ocaml.body_scaled(obj,scale))

        self.obj = new_obj                           # update current object

        # bounding box is NOT updated


    def unite(self,other):
        """unite( obj ).

        Function to take the union of the
        mesh object obj with the present object.
        """
        new_obj = mesh.mesh_obj()                         # create new object
        for other_obj in other.obj:
            for obj in self.obj:
                new_obj.obj.append(ocaml.body_union([obj,other_obj]))

        for i in range(len(self.bbox[0])):           # update bounding box       
            new_obj.bbox[0] = self.bbox[0][:]
            new_obj.bbox[1] = self.bbox[1][:]

#        print new_obj.bbox
        return new_obj

    def intersect(self,other):
        """intersect( obj ).

        Function to take the intersection of the
        mesh object obj with the present object.
        """
        new_obj = []                                 # create new object
        for other_obj in other.obj:
            for obj in self.obj:
                new_obj.append(ocaml.body_intersection([obj,other_obj]))

        self.obj = new_obj                           # update current object

        # No need to update bounding box


    def __add__(self, other):
        """(+).

        Function to add an object or shift the present object 
        """
        new_obj = mesh.mesh_obj()                    # create new object
        new_obj.obj = self.obj[:]                    # copy current object

        for i in range(len(self.bbox[0])):           # update bounding box 
            new_obj.bbox[0].append(self.bbox[0][i])
            new_obj.bbox[1].append(self.bbox[1][i])

        if type(other) == type([0.0,0.0]):           # shift the new object
            new_obj.shift(shifting=other)
        elif type(other.obj[0]) == type(self.obj[0]):# add another object
            for other_obj in other.obj:              # update new object
                new_obj.obj.append(other_obj)
        else:
            raise TypeError('Cannot handle type')

        return new_obj

    __radd__ = __add__

    def __sub__(self, other):
        """ (-).

        Function to take the difference between two objects
        """

        new_obj = mesh.mesh_obj()                    # create new object

        for sub_obj in other.obj:
            for obj in self.obj:
                new_obj.obj.append( ocaml.body_difference(obj,[sub_obj])) 
                
        for i in range(len(self.bbox[0])):           # update bounding box       
            new_obj.bbox[0].append(self.bbox[0][i])
            new_obj.bbox[1].append(self.bbox[1][i])
            
        return new_obj
        
    def __mul__(self, other):
        import Numeric
        new_obj = mesh.mesh_obj()                    # create new object
        new_obj.obj = self.obj[:]                    # copy current object

        for i in range(len(self.bbox[0])):           # update bounding box 
            new_obj.bbox[0].append(self.bbox[0][i])
            new_obj.bbox[1].append(self.bbox[1][i])

        if type(other) == type(0) and other >= 1:    # add another object
            for times in range(1,other):
                shift_list = list(times*Numeric.array(self.shifting))
                tmp_obj = self.copy()
                tmp_obj.shift(shifting=shift_list)
                for add_obj in tmp_obj.obj:
                    new_obj.obj.append(add_obj) 
        else:
            raise TypeError('Cannot handle type')

        return new_obj

    __rmul__ = __mul__
    
    def copy(self):
        new_obj = mesh.mesh_obj()                    # create new object

        new_obj.obj = self.obj[:]                    # update new object

        new_obj.bbox[0] = self.bbox[0][:]            # update bounding box
        new_obj.bbox[1] = self.bbox[1][:] 

#        print new_obj.bbox
        return new_obj

    def _in2circ(self, ccradii, icradii, mode=2):
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
        import Numeric, numarray
        
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


    def _findAngles(self,meshData):
        """This function works out the angles in all triangles of a 2D mesh,
        and all the faces of tetrahedra in a 3D mesh. In an ideal mesh all
        these angles would be 60 degrees.
        
        Author: James Kenny              Last modified: 16/03/06
        Filename: meshviz.py
        
        Input: meshinfo   (uses: list of points for 2D/3D mesh)
        list of triangles making 2D/3D mesh
        
        Output: array of internal angles of triangles (or tetrahedra faces)
        
        """
        import Numeric, math

        # extract the useful information
        points = meshData[0][2]
        cells = []        

        for i in meshData[2][2]:
            cells.append(i[0])

        def computeTriangle(tri):
            """This is a nested function which computes the angles in a triangle
            or on the face of a tetrahedron.
            
            Could employ dot product or cosine & sine rules.
            
            Input: three references to points in array 'cells'
            Output: three angles in degrees (list)
            """

            # define three rotations of the same triangle so that the same
            # algorithm can be used to find each angle
            a = points[tri[0]]; b = points[tri[1]]; c = points[tri[2]]
            tris = [[a, b, c], [b, c, a], [c, b, a]]
            angles = []
            
            for i in tris:
                # define 2 vectors representing 2 sides of the triangle
                # either side of the angle to be calculated
                r_ab = Numeric.transpose(i[1]) - i[0]
                r_ac = Numeric.transpose(i[2]) - i[0]
                
                # calculate the angle between the two sides
                rdotr = Numeric.dot(r_ab, r_ac)
                modrr = math.sqrt(sum(r_ab**2))*math.sqrt(sum(r_ac**2))
                
                angle = math.degrees(math.acos(rdotr / modrr))
                angles.append(angle)
                
#                tangles = Numeric.zeros([3],Numeric.Float32)
#            print len(angles)
#            print angles[0], angles[1], angles[2]
            tangles = [angles[0], angles[1], angles[2]]
            return tangles

        # determine if we have been given a 2D or 3D mesh
        if len(cells[0]) == 3:
            # we are dealing with triangles
            angles = Numeric.zeros([len(cells),3],Numeric.Float32)        
            for i in range(len(cells)):
                angles[i] = computeTriangle(cells[i])  
            
        if len(cells[0]) == 4:
            # we are dealing with tetrahedra
            angles = Numeric.zeros([len(cells),4,3],Numeric.Float32)
            for i in range(len(cells)):

                angles[i][0] = computeTriangle([cells[i][0],cells[i][1],cells[i][3]])
                angles[i][1] = computeTriangle([cells[i][1],cells[i][2],cells[i][3]])
                angles[i][2] = computeTriangle([cells[i][2],cells[i][3],cells[i][0]])
                angles[i][3] = computeTriangle([cells[i][0],cells[i][1],cells[i][2]])
   
        return Numeric.ravel(angles)



    def _mesh2vtk(self,mesh,save_vtk,nr_piece="",n=""):
        """This function converts the appropriate data from the
        mesh info arrays output from the mesher, into
        vtkUnstructuredGrids ready for visualisation in MayaVi.
        Uses PyVTK.

        Automatically chooses between 2D and 3D meshes.
        1D may be covered later.

        Can ask for in2circ data to be calculated.
        """
        import tempfile, os, vtkpython, pyvtk, Numeric

#        print "****************** mesh2vtk *******************",save_vtk
        
        if save_vtk !="":
#            print "-----------------------------------"
            file_name = save_vtk[:-4]+nr_piece+n+".vtk"
        else:
            # workaround to avoid writing to files on disk all the time
            # write to a fake temporary file and read from there
            # vtk-python data structures are not identical in memory!
#            print "...................................."
            file_name = tempfile.mktemp(suffix='.vtk')


#        print "mesh2vtk --- 1"
        reader = vtkpython.vtkUnstructuredGridReader()

#        print "mesh2vtk --- 2"
        # decide if this is a 2D or 3D mesh
        dim = len(mesh[0][2][0])
        if dim == 0 or dim > 3:
            raise ValueError, "Mesh should be 2D or 3D." 
        else:
            print "Dimension of the space is %d" % (dim)
#        print "mesh2vtk --- 3"


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
            in2circData = self._in2circ(ccradii, icradii)
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
            in2circData = self._in2circ(ccradii, icradii)
            data.cell_data.append(pyvtk.Scalars(in2circData, "in2circ"))


        data.tofile(file_name, format='ascii')
        reader.SetFileName(file_name)
        reader.Update()
        if save_vtk =="":
            os.remove(file_name)
        
        return reader.GetOutput()

class box(mesh_obj):
    """Class to create a bounded box
    """
    
    def __init__(self, coords=[],shifting=[], outer_box = [], sc = True):
        """bbox(coords:[float list, float list], shifting:float list,
        outer_box:[float list, float list], sc:bool).
        Creates a box given the coordinates of the lower-left and
        upper_right vertices. The box is shifted to the position
        shifting wrt the origin of coordinates system.
        If sc = False, the shift is wrt the centre of the box.
        """
        mesh_obj.__init__(self)

        if coords == [] and shifting != []:          # only shifting is given
            tmp0_list = []
            tmp1_list = []
            for i in range(len(shifting)):
                tmp0_list.append(0.0)
                tmp1_list.append(1.0)
            coords = [tmp0_list, tmp1_list]

        elif coords != [] and shifting == []:        # only coords is given
            for i in range(len(coords[0])):
                shifting.append(0.0)
        elif coords == [] and shifting == []:        # default: 2D
            tmp0_list = []
            tmp1_list = []
            for i in range(2):
                tmp0_list.append(0.0)
                tmp1_list.append(1.0)
                shifting.append(0.0)
            coords = [tmp0_list, tmp1_list]
        else:
            pass

        print "box"
        print coords, shifting

        if sc:                                       # system coordinates
            self.obj.append(ocaml.body_shifted_sc(ocaml.body_box(coords[0],coords[1]),shifting))
        else:                                        # body coordinates
            self.obj.append(ocaml.body_shifted_bc(ocaml.body_box(coords[0],coords[1]),shifting))
            

        min_coords = []                              # create bounding box  
        max_coords = []

        for i in range(len(shifting)):
            if outer_box == []:
                min_coords.append(min(coords[0][i]+shifting[i],coords[1][i]+shifting[i]))
                max_coords.append(max(coords[0][i]+shifting[i],coords[1][i]+shifting[i]))
            else:
                min_coords.append(min(coords[0][i]+shifting[i],coords[1][i]+shifting[i], outer_box[0][i], outer_box[1][i]))
                max_coords.append(max(coords[0][i]+shifting[i],coords[1][i]+shifting[i],outer_box[0][i], outer_box[1][i]))

        self.bbox = [min_coords, max_coords]         # update bounding box   
        print "bbox"
        print self.bbox
        print "box.\n"        
        
class ellipsoid(mesh_obj):
    """Class to create an ellipsoid
    """
    
    def __init__(self,length=[],shifting=[], outer_box = [], sc = True):
        """ellipsoid(length: float list, shifting: float list,
        outer_box:[float list, float list], sc:bool).
        Creates an ellipsoid given the length of
        the main axes. The ellipsoid is shifted to the position shifting
        wrt the origin of coordinates system. If sc = False, the shift
        is wrt the centre of the ellipsoid
        """
        mesh_obj.__init__(self)

        if length == [] and shifting != []:          # only shifting is given
            for i in range(len(shifting)):
                length.append(1.0)
                
        elif length != [] and shifting == []:        # only length is given
            for i in range(len(length)):
                shifting.append(0.0)
        elif length == [] and shifting == []:        # default: 2D
            for i in range(2):
                length.append(1.0)
                shifting.append(0.0)
        else:
            pass

        print "ellips"
        print length , shifting
        if sc:                                       # system coordinates
            self.obj.append(ocaml.body_shifted_sc(ocaml.body_ellipsoid(length),shifting))
        else:                                        # body coordinates
            self.obj.append(ocaml.body_shifted_bc(ocaml.body_ellipsoid(length),shifting))


        min_coords = []                              # create bounding box
        max_coords = []

        for i in range(len(shifting)):
            if outer_box == []:
                min_coords.append(-length[i]+shifting[i])
                max_coords.append(length[i]+shifting[i])
            else:
                min_coords.append(min(-length[i]+shifting[i], outer_box[0][i], outer_box[1][i]))
                max_coords.append(max(length[i]+shifting[i],outer_box[0][i], outer_box[1][i]))

        self.bbox = [min_coords, max_coords]          # update bounding box   
        print "bbox"
        print self.bbox
        print "ellips.\n"


class conical(mesh_obj):
    """Class to create a conical frustum
    """
    
    def __init__(self,coords1=[],rad1=1.0,coords2=[],rad2=0.0,shifting=[],
                 outer_box = [], sc = True):
        """conical( coords1:float list, rad1:float, coords2: float list,
        rad2: float, shifting: float list, outer_box:[float list, float list],
        sc:bool).
        Creates a conical frustum given the centre of
        the bottom circumference, its radius, the upper circumference
        and its radius. The frustum is shifted to the position shifting
        wrt the origin of coordinates system. If sc = False, the shift
        is wrt the centre of the ellipsoid
        """
        mesh_obj.__init__(self)
        
        if coords1 == [] and shifting != []:          # only shifting is given
            for i in range(len(shifting)):
                coords1.append(0.0)
                coords2.append(0.0)
            coords2[-1] = 1.0 
            
        elif coords1 != [] and shifting == []:        # only coords is given
            for i in range(len(coords[0])):
                shifting.append(0.0)
        elif coords1 == [] and shifting != []:        # default: 2D
            for i in range(2):
                coords1.append(0.0)
                coords2.append(0.0)
                shifting.append(0.0)
            coords2[-1] = 1.0 
        else:
            pass

        print "cone"
        print coords1, coords2, shifting


        if sc:                                       # system coordinates
            self.obj.append(ocaml.body_shifted_sc(ocaml.body_frustum(coords1,rad1,coords2,rad2),shifting))
        else:                                        # body coordinates
            self.obj.append(ocaml.body_shifted_bc(ocaml.body_frustum(coords1,rad1,coords2,rad2),shifting))


        min_coords = []                              # create bounding box
        max_coords = []

        import Numeric
        c1 = Numeric.array(coords1)
        c2 = Numeric.array(coords2)
        max_dim = max(rad1, rad2, Numeric.sqrt(Numeric.add.reduce((c1-c2)*(c1-c2))))
        
        for i in range(len(shifting)):
            if outer_box == []:
                min_coords.append(shifting[i]-max_dim/2.)
                max_coords.append(shifting[i]+max_dim/2.)
            else:
                min_coords.append(min(length[i]+shifting[i], outer_box[0][i], outer_box[1][i]))
                max_coords.append(max(shifting[i]+max_dim/2.,outer_box[0][i], outer_box[1][i]))

        self.bbox = [min_coords, max_coords]          # update bounding box   
        
        print "bbox"
        print self.bbox
        print "cone.\n"


def load_mesh(file_name = ""):
    """read(file_name:string).

    Function to load a mesh from the file file_name.
    """
    raw_mesh = ocaml.mesh_readfile(file_name) # read mesh
    
    mesh_info = ocaml.mesh_plotinfo(raw_mesh)  # extract data from the mesh
    print "read mesh: ok"
    return mesh_info 
