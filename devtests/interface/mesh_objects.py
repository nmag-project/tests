import ocaml
import mesh_objects
import types
class mesh_obj:
    def __init__(self, dim, fixed_points):
        """Base class of a mesh object
        """
        #-------------------------------------
        # self.obj IS an OCaml PILL
        #-------------------------------------

        self.dim = dim
        self.fxd_pts = fixed_points 
        
    def shift(self, shift, sc=True ):
        """shift(
        shift:float list   -  shifting vector to add to the current position   
        sc:bool            -  reference system for shifting (body or system coordinates)
        ).

        Function to shift the object of the amount shift along
        the axes. If sc = False the shift is made wrt the body
        coordinates, wrt the system coordinates otherwise.
        """

        if sc:  
            self.obj = ocaml.body_shifted_sc(self.obj,shift)
        else:
            self.obj = ocaml.body_shifted_bc(self.obj,shift)

    def scale(self, scale):
        """scale(
        scale:float list  - scaling factors along the axes of the object
        ).
        
        Function that scales the object along the axes
        with the factors given by the scale vector
        """
        if sc: 
            self.obj = ocaml.body_scaled(self.obj,scale)

    def rotate(self, a1_ix, a2_ix, ang=0.0, sc=True):
        """rotate(
        a1_ix:int -  index of first rotation axis 
        a2_ix:int -  index of second rotation axis
        ang:float -  angle of rotation (degrees)
        sc:bool   -  reference system for rotation (body or system coordinates)
        ).

        Function that rotates the object of an angle ang
        given the indices of the rotation axes.
        If sc = False the rotation is made wrt the
        body coordinates, wrt the system coordinates otherwise.        
        """

        if sc:
            self.obj = ocaml.body_rotated_sc(self.obj,a1_ix,a2_ix,ang) 
        else:
            self.obj = ocaml.body_rotated_bc(self.obj,a1_ix,a2_ix,ang)  

    def rotate2d(self, ang=0.0, sc=True):
        """rotate(
        ang:float -  angle of rotation (degrees)
        sc:bool   -  reference system for rotation (body or system coordinates)
        ).

        Function that rotates the 2D object of an angle ang.
        If sc = False the rotation is made wrt the
        body coordinates, wrt the system coordinates otherwise.        
        """
        if sc:
            self.obj = ocaml.body_rotated_sc(self.obj,0,1,ang) 
        else:
            self.obj = ocaml.body_rotated_bc(self.obj,0,1,ang)  

    def rotate3d(self, axis, ang=0.0, sc=True):
        """rotate(
        axis:float list  -  rotation axis 
        ang:float        -  angle of rotation (degrees)
        sc:bool          -  reference system for rotation (body or system coordinates)
        ).

        Function that rotates the 3D object of an angle ang
        wrt to the given axis.
        If sc = False the rotation is made wrt the
        body coordinates, wrt the system coordinates otherwise.        
        """
        if sc:
            self.obj = ocaml.body_rotated_axis_sc(self.obj,axis,ang) 
        else:
            self.obj = ocaml.body_rotated_axis_bc(self.obj,axis,ang)   

    def unite(self,obj):
        """unite( obj ).

        Function to take the union of the
        mesh object obj with the present object.
        The argument obj can also be a list of objects.
        The present object is updated in-place.
        """

        try:
            if type(obj.obj) == type(self.obj):
                other_obj = obj
        except:
            raise TypeError("Type mismatch for object union")

        self.obj = ocaml.body_union([self.obj,other_obj.obj])

    def subtract(self,obj):
        """subtract( obj ).
        
        Function to take the difference between the
        present object and the object obj.
        The present object is updated in-place.
        """
        
        try:
            if type(obj.obj) == type(self.obj):
                other_obj = obj
        except:
            raise TypeError("Type mismatch for object difference")

        self.obj = ocaml.body_difference(self.obj,[other_obj.obj])

    def intersect(self,obj):
        """intersect( obj ).
        
        Function to take the intersection of the
        mesh object obj with the present object.
        Only one object can be intersected with
        the present object.
        """

        try:
            if type(obj.obj) == type(self.obj):
                other_obj = obj
        except:
            raise TypeError("Type mismatch for object intersection")

        self.obj = ocaml.body_intersection([self.obj,other_obj.obj])

        
    def __add__(self, other):
        """(+).

        Function to unite an object or shift the present object 
        """

        if type(other) == types.ListType:                 # shift the new object
            shift = other
            new_obj = mesh_objects.mesh_obj(self.dim)     # create new object
            new_obj.obj = self.obj                        # copy present object in the new one
            new_obj.shift(shifting=shift)                 # update new object
            return new_obj
            
        elif type(other.obj) == type(self.obj):           # unite the new object to the present one
            other_obj = other
            new_obj = mesh_objects.mesh_obj(self.dim)     # create new object
            new_obj.obj = self.obj                        # copy present object in the new one
            new_obj.unite(other_obj)                          # update new object
            return new_obj
                
        else:
            raise TypeError, "Cannot handle object type"


    __radd__ = __add__

    

    def __sub__(self, obj):
        """ (-).

        Function to take the difference between two objects
        """

        try:
            if type(obj.obj) == type(self.obj):
                other_obj = obj
        except:
            raise TypeError("Type mismatch for object difference")
            
        new_obj = mesh_objects.mesh_obj(self.dim)         # create new object
        new_obj.obj = self.obj                            # update new object 
        new_obj.difference(other_obj)          
        return new_obj   
                

#    def set_shift(self,shifting = []):
#        if shifting == []:
#            for i in range(self.dim):
#                shifting.append(0.0)
#        self.shifting = shifting 
#
#    def __mul__(self, other):
#        import Numeric, copy
#        
#        new_obj = mesh_objects.mesh_obj(self.dim)    # create new object
#        new_obj.obj = self.obj                       # copy current object
#
#        if type(other) == types.IntType and other >= 1:    # add another object
#            for times in range(1,other):
#                shift_list = list(times*Numeric.array(self.shifting))
#                print shift_list
#                print "self copy NOW!!!"
#                tmp_obj = self.copy()
#                print "self copy DONE!!!"
#                print self, tmp_obj
#                tmp_obj.shift(shifting=shift_list)
#                for add_obj in tmp_obj.obj:
#                    new_obj.obj.append(add_obj) 
#        else:
#            raise TypeError('Cannot handle type')
#
#        return new_obj
#
#    __rmul__ = __mul__
#    
#    def replicate(self):
#        new_obj = mesh_objects.mesh_obj(self.dim)    # create new object
#
#        new_obj.obj = self.obj                       # update new object
#
#        return new_obj

    def transformations(transform, sc):
        """ Function to perform transformation on the object
        following the order specified in the transform list.
        If sc = False the transformations are made wrt the
        body coordinates, wrt the system coordinates otherwise.        
        """
        
        if transform not []:                         # perform transformations on the object 
            while len(transform) > 0:
                tra = transform[0][0]
                arg1 = transform[0][1]
                try:
                    arg2 = transform[0][2]
                except:
                    pass

                if tra == "shift":
                    self.shift(arg1)
                elif tra == "scale":
                    self.scale(arg1)  
                elif tra == "rotate":
                    self.rotate(arg1[0],arg1[1],arg2)
                elif tra == "rotate2d":
                    self.rotate2d(0,1,arg1)
                elif tra == "rotate3d":
                    self.rotate3d(arg1,arg2)
                else:
                    try:
                        print tra,': invalid transformation', arg1, arg2
                    except:
                        print tra,': invalid transformation', arg1 
                    sys.exit(1)
                del transform[0] 

class box(mesh_obj):
    """Class to create a bounded box
    """
    
    def __init__(self, coords, transform=[], fixed_points=[], sc = True):
        """box(
        coords:[float list, float list],
        transform:(string, transformation_data) list,
        fixed_points: float list list ,
        sc:bool
        ).
        
        Creates a box given the coordinates of the lower-left and
        upper_right vertices. The box is transformed following the order
        of the transformations specified in the transform list.
        Calling ai (i = 1,2,...) the axis of the space where the object is
        defined, examples of these transformations are:
        - ("shift", [a1,a2,a3,..]) 
        - ("scale", [a1,a2,a3,...])
        - ("rotate", [a1,a2], phi)
        - ("rotate2d", phi)
        - ("rotate3d", [a1,a2,a3], phi)
        If sc = False the transformations are made wrt the body coordinates,
        wrt the system coordinates otherwise.
        """

        dim = len(coords[0]) 
        mesh_obj.__init__(self, dim, fixed_points)
        
        print "create box"
        self.obj = ocaml.body_box(coords[0],coords[1])

        self.transformations(transform,sc)

class ellipsoid(mesh_obj):
    """Class to create an ellipsoid
    """
    
    def __init__(self, length=[], transform=[], fixed_points=[], sc = True):
        """ellipsoid(length: float list, transform:(string, transformation_data) list,
        fixed_points: float list list , sc:bool).
        
        Creates an ellipsoid given the length of
        the main axes. The ellipsoid is transformed following the order
        of the transformations specified in the transform list.
        Calling ai (i = 1,2,...) the axis of the space where the object is
        defined, examples of these transformations are:
        - ("shift", [a1,a2,a3,..]) 
        - ("scale", [a1,a2,a3,...])
        - ("rotate", [a1,a2], phi)
        - ("rotate2d", phi)
        - ("rotate3d", [a1,a2,a3], phi)
        If sc = False the transformations are made wrt the body coordinates,
        wrt the system coordinates otherwise.
        """

        dim = len(length) 
        mesh_obj.__init__(self,dim, fixed_points)
        
        print "ellips"
        self.obj = ocaml.body_ellipsoid(length)

        self.transformations(transform,sc)

class conical(mesh_obj):
    """Class to create a conical frustum
    """
    
    def __init__(self, coords1=[], rad1=1.0, coords2=[], rad2=0.0, transform=[], fixed_points=[], sc = True):
        """conical( coords1:float list, rad1:float, coords2: float list, rad2: float,
        transform:(string, transformation_data) list, fixed_points: float list list , sc:bool).
        
        Creates a conical frustum given the centre of
        the bottom circumference, its radius, the upper circumference
        and its radius. The frustum is transformed following the order
        of the transformations specified in the transform list.
        Calling ai (i = 1,2,...) the axis of the space where the object is
        defined, examples of these transformations are:
        - ("shift", [a1,a2,a3,..]) 
        - ("scale", [a1,a2,a3,...])
        - ("rotate", [a1,a2], phi)
        - ("rotate2d", phi)
        - ("rotate3d", [a1,a2,a3], phi)
        If sc = False the transformations are made wrt the body coordinates,
        wrt the system coordinates otherwise.
        """

        dim = len(coords1) 
        mesh_obj.__init__(self,dim)

        print "cone"
        self.obj = ocaml.body_frustum(coords1,rad1,coords2,rad2)

        self.transformations(transform,sc)
