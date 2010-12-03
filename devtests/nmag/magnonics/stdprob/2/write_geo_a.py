prob_descr = """
Description: Permalloy elements 12nm x 12nm x 3nm, separation:

    A) 3 nm (1D lattice with 15 nm periodicity, monoelement base)

    B) 3 and 6 nm alternating (1D lattice with 33 nm periodicity, and
       2-elements base), 30 elements in the chain (or infinite chain,
       according to the method)

Excitation (if needed): the leftmost element with a Gaussian pulse (10ps FWHM).
Ms = 860 emu/cc, A = 1.3 x 1011 J/m, K = 0, g = 2.1, alfa = 0
Bias field applied parallel and perpendicular to the long axis.
Suggested cell size: 3 nm x 3 nm x 3 nm (other cases can be added to this one)
"""

maxh = 3.0
blockx, blocky = 12,12 #nm
blockz = 3 #nm
spacingx = 3 #nm
periodx = spacingx+blockx
#total number of blocks

f = open('a.geo', 'w')

allsolid = "solid cube="

f.write("#cube %d\nalgebraic3d\n" % (15))
for i in range(0,30):
    xpos1 = i*periodx-0.5*blockx
    xpos2 = i*periodx+0.5*blockx
    ypos1  = -blocky/2.
    ypos2  =  blocky/2.
    zpos1  = -blockz/2.
    zpos2  =  blockz/2.

    allsolid += "cube%02d or " % i


    cubestr2 = """solid cube%02d=orthobrick(%g, %g, %g; %g, %g, %g);\n\n""" % \
               (i,xpos1,ypos1,zpos1,xpos2,ypos2,zpos2)

    f.write(cubestr2)

f.write("\n%s -maxh=%f;\ntlo cube;\n" % (allsolid[:-4], maxh))
f.close()

