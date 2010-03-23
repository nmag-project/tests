"""
This file generates the meshes geometries (netgen) for the 2nd mumag
standard problem.
All distances here are measured in nanometers.
"""

import material
from nmag import simulation_units as su
from nmag import SI
import nsim.sets as sets

# This is the list of values for d/l_ex.
# For each of these value a mesh geometry specification file .geo
# will be generated. This file can be used with netgen to obtain
# the meshes. Unfortunately it seems one has to do it manually
# Then use 'make convert' to pass from neu to h5 mesh file format.
d_list = sets.float_set([5, 10, "...", 30]) # values of d/lex

def create_mesh(d, file_name, rod=None):
    L, d, t = material.bar_size(d)
    if rod == None:
        rod = t
    else:
        rod = min(rod, t)
    s = "algebraic3d\nsolid cube = plane (0, 0, 0; 0, 0, -1)\n"
    s += "  and plane (0, 0, 0; 0, -1, 0)\n  and plane (0, 0, 0; -1, 0, 0)\n"
    s += "  and plane (%f, %f, %f; 0, 0, 1)\n" % (L, d, t)
    s += "  and plane (%f, %f, %f; 0, 1, 0)\n" % (L, d, t)
    s += "  and plane (%f, %f, %f; 1, 0, 0) -maxh = %f;\ntlo cube;\n"  % (L, d, t, rod)
    f = open(file_name, "w")
    f.write(s)
    f.close()

def mesh_file(d, extension="geo"):
    """Given d, return the corresponding mesh file."""
    return "film_d%03d.%s" % (d, extension)

def better_mesh(d):
    """This function returns the mesh which better represents the film
       having the given width d (d is non dimensional: it expresses
       the width of the film in unit of the exchange lenght)"""
    for try_d in d_list:
        if d < try_d+0.5:
            return (mesh_file(try_d, extension="h5"), d/try_d)

if __name__ == "__main__":
    l_ex = su.of(material.exchange_length)
    meshes = [ (d*l_ex, mesh_file(d)) for d in d_list ]
    for (d, file_name) in meshes:
        create_mesh(d, file_name, rod=0.15*l_ex)
