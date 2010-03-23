""" Mesh class. The purpose of this module is to have
    an interface which hides all the OCaml calls to the
    mesh generator. 
    
    Author: Giuliano Bordignon
    Last modified: 12/04/06
"""
from __future__ import division
import mesh as mesh_module
#from mesh_objects import *
import ocaml 
import types

class mesh:
    def __init__(self, objects = [], rod_length = 0.5, bbox = [[],[]],
                 density="", periodic = False, visual = False, fixed_points = [],
                 fun=[], fun_call_interval = 1000):

        """ Class to define the parameters for the meshing algorithm.
        mesh(
        objects:obj list              - objects to be meshed
        rod_length:float              - desired length of connection between nodes
        bbox:[float list,float list]  - outer bounding box
        density:string                - density function of nodes ditribution 
        periodic:bool                 - periodic boundary conditions in the outer box 
        visual:bool                   - use of the visualisation package
        fixed_points: float list list - set of fixed points to be used in the mesh
        fun                           - function to be called every interval steps
        fun_call_interval:int         - interval of the function calling
        ).
        
        The rod_length is the desired length of the connections between
        the mesh nodes, a value which is weighted with the density function
        (given in C code). The bbox defines the outer boundary box of the mesh.
        The function fun is executed every fun_call_interval steps and its
        arguments are

        nr_piece       =  index of the meshing object
        iteration_nr   =  number of iteration in the relaxation process
        mesh           =  mesh as a python list of lists (value returned by mesh_it())
        
        The visual flag and the periodic flag are used to visualise and impose
        periodic boundary conditions on the outer box, respectively.
        If periodic boundary conditions are used, the density function
        must respect the related contraints.
        """

        self.obj = []
        if type(objects) == types.ListType :
            for obj in objects:
                self.obj.append(obj.obj)
        else:
            raise ValueError("Error: wrong list of objects to mesh.")
        self.rod = rod_length
        self.bbox = bbox
        self.density = density
        if periodic:
            self.periodic = 1
        else:
            self.periodic = 0
        if visual:
            #import m.visual
            pass
        if fun == []:
            self.fun_driver = self._default_fun
        else:
            self.fun_driver = fun
        self.fun_call_interval = fun_call_interval

        self.fixed_points = fixed_points
        # add fixed points coming from objects
        for obj in objects:
            for pt in obj.fxd_pts:
                self.fixed += pt

        self.mesher = 0                         # flag for default/copied mesher
        self.my_mesher = ocaml.mesher_defaults  # default mesher
        self.driver = ocaml.make_mg_gendriver(self.fun_call_interval, self.extended_fun_driver)
        self.raw_mesh = []

    def default_fun(self,nr_piece,n,mesh):
        """Default function for the driver
        """
        pass
        
    def check_mesher(self):
        """check_mesher().
        
        Function to create a copy of the mesher.
        The parameters of this mesher can be modified.        
        """
        if self.mesher == 0:
            self.my_mesher = ocaml.copy_mesher_defaults(ocaml.mesher_defaults)
            self.mesher = 1
            
    def frequency(self,new_frequency = 0):
        """frequency( new_frequency:int ).

        Function to change the number
        of steps for the execution of the function f
        """
        self.frequency = new_frequency


    def fixed_points(self, fixed = []):
        """List of points used as fixed points for the mesh
        """
        if fixed != []:
            self.fixed += fixed
    
    def default_fun(self,nr_piece,n,mesh):
        """Default function for the driver
        """
        pass

    def extended_fun_driver(self,nr_piece,iteration_nr,mesh):
        """
        Change the function to be executed every fun_call_interval steps.
        """
        self.fun_driver(nr_piece,iteration_nr,mesh)
        if self.visual:
            # call to the visual module
            pass
        
    def mesh_it(self, mesh):
        
                
        print "Fixed points:", mesh.fixed_points
        print "*********************************************"

        mesh.raw_mesh = ocaml.mesh_bodies_raw(mesh.driver,mesh.my_mesher, mesh.bbox[0],mesh.bbox[1], 1,\
                                         mesh.obj,mesh.rod,mesh.density,mesh.periodic,mesh.fixed_points)
        
        # return the ocaml mesh 
        return mesh.raw_mesh

    def inspect(self, mesh):
        
        mesh_info = ocaml.mesh_plotinfo(mesh.raw_mesh)  # extract data from the mesh
        return mesh_info 

    def plot2d_ps(self, file_name="", scale_x=50,scale_y=50,offset_x=300,offset_y=300):
        """
        Function to save a 2D mesh on a postscript file.
        """
        sc_x = float(scale_x)
        sc_y = float(scale_y)
        os_x = float(offset_x)
        os_y = float(offset_y)
        
        ocaml.mesh2d_ps(self.raw_mesh,file_name,[sc_x,sc_y,os_x,os_y])

    def plot_vtk(self, file_name=""):
        pass

    def plot2D_png(self, file_name=""):
        pass
        
    def set_max_relaxation(self,scale = 3.0):
        """set_scaling_movement( scale:float ).

        Function to change
        the behaviour of the mesh algorithm at the beginning of the
        mesh generation. It increases the max displacement before a
        re-triangulation, the time_step and the topology threshold
        """
        self.check_mesher()
        self.scaling_movement = scale
        ocaml.mesher_defaults_set_tolerated_rel_movement(self.my_mesher,self.scaling_movement)

    def set_topology_threshold(self,thresh = 0.2):
        """set_topology_threshold( thresh:float ).

        Function to change
        the default value of the topology threshold. The mesher
        re-triangulates if the movement of one of the points exceeds
        this value.
        """
        self.check_mesher()
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

        self.check_mesher()
        self.scaling_time_step = scale
        ocaml.mesher_defaults_set_time_step_scale(self.my_mesher,self.scaling_time_step)

    def set_tolerated_rel_move(self,scale = 0.004):
        """set_tolerated_rel_move( scale:float ).

        Function to change
        the default value of the tolerated relative movement.
        The mesher stops when the relative movement of all the points
        is within this value. 
        """

        self.check_mesher()
        self.scaling_tolerated_move = scale
        ocaml.mesher_defaults_set_tolerated_rel_movement(self.my_mesher, self.scaling_tolerated_move)

    def load_mesh(self, mesh, file_name = ""):
        """load_mesh(file_name:string).
        
        Function to load a mesh from the file file_name.
        """

        new_mesh = mesh_module.mesh()
        new_mesh.raw_mesh = ocaml.mesh_readfile(file_name) # read mesh
        print "read mesh: ok"
        return new_mesh
            
    def save_mesh(mesh, file_name = ""):
        """save_mesh(mesh, file_name:string).
        
        Function to save a mesh on the file file_name.
        """
        ocaml.mesh_writefile(file_name,mesh.raw_mesh)
        """
        
        """

        """Possible formats are postscript file(s) ("ps" extension) (2D only),
        vtk file(s) ("vtk" extension) (included the ones created at every
        visualization step) and "pyfem" format ("dat" extension).
        The function returns the mesh data in a python list of lists
        (the content is clear once they are inspected).
        """
        print "saved mesh: ok"
 
