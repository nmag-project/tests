import math
import numpy

#global parameter for the height of our pyramid. We consider a special case
#of pyramids for which the edgelength is twice as long as the the height.
  
h=300.0

#global parameter for the width w of the pyramid shell

w=60.0

#this parameter is the maximal tetraeder edge length of our finite element grid.
#for Nickel the exchange length is equal to 6.861 nm (according to Richard
#Boardman's database)

hmax=3.4


def build_pyramid_shell(edgelength=50.0,height=40.0,width=5.0,elementlength=3.4):
    """This function creats the Netgen Geometry File for a pyramid shell.
    The parameters edgelength and height determine the structure of the
    inner pyramid. Width is the width of the shell measured perpendicular
    to the normal of the faces."""
    edgelength = float(edgelength)
    height = float(height)
    width = float(width)
    elementlength=float(elementlength)
    
    #introducing width2, which is measured parallel to the pyramid's basis face
    width2 = width / math.cos(math.atan(2*height/edgelength))

    print "Defining the corners of the structure.\n"
    cor1 = numpy.array([0.0,0.0,0.0],dtype=float)
    cor2 = numpy.array([edgelength,0.0,0.0],dtype=float)
    cor3 = numpy.array([0.0,edgelength,0.0],dtype=float)
    cor4 = numpy.array([edgelength,edgelength,0.0],dtype=float)
    top = numpy.array([edgelength/2.0,edgelength/2.0,height])

    print "Defining the surfaces of the pyramid.\n"

    print "Bottom face:\n"
    bottom_point = cor1
    bottom_vec = numpy.cross(cor3,cor2)
    bottom_vec = bottom_vec / math.sqrt(numpy.dot(bottom_vec,bottom_vec))

    print "Faces of the inner pyramid:\n"
    face1_point = cor1
    face1_vec = numpy.cross((cor2-cor1),(top-cor1))
    face1_vec = face1_vec / math.sqrt(numpy.dot(face1_vec,face1_vec))

    face2_point = cor2
    face2_vec = numpy.cross((cor4-cor2),(top-cor2))
    face2_vec = face2_vec / math.sqrt(numpy.dot(face2_vec,face2_vec))

    face3_point = cor4
    face3_vec = numpy.cross((cor3-cor4),(top-cor4))
    face3_vec = face3_vec / math.sqrt(numpy.dot(face3_vec,face3_vec))

    face4_point = cor3
    face4_vec = numpy.cross((cor1-cor3),(top-cor3))
    face4_vec = face4_vec / math.sqrt(numpy.dot(face4_vec,face4_vec))


    print "Faces of the outer pyramid\n"
    face5_point = cor1 + numpy.array([-width2,-width2,0.0])
    face5_vec = face1_vec

    face6_point = cor2 + numpy.array([width2,-width2,0.0])
    face6_vec = face2_vec

    face7_point = cor4 + numpy.array([width2,width2,0.0])
    face7_vec = face3_vec

    face8_point = cor3 + numpy.array([-width2,width2,0.0])
    face8_vec = face4_vec


    print "Creating the file pyramid_shell.geo"

    outputfile = open("pyramid_shell.geo","w")
    outputfile.write("#Pyramid, Height: %f, Edge Length: %f\n" % (height,edgelength))
    outputfile.write("algebraic3d\n")

    print "Defining the inner pyramid:\n"
    outputfile.write("solid innerpyramid = plane(%f,%f,%f; %f,%f,%f)\n" \
                     % (bottom_point[0],bottom_point[1],bottom_point[2],\
                        bottom_vec[0],bottom_vec[1],bottom_vec[2]))
    outputfile.write("and plane(%f,%f,%f; %f,%f,%f)\n" \
                     % (face1_point[0],face1_point[1],face1_point[2],\
                        face1_vec[0],face1_vec[1],face1_vec[2]))
    outputfile.write("and plane(%f,%f,%f; %f,%f,%f)\n" \
                     % (face2_point[0],face2_point[1],face2_point[2],\
                        face2_vec[0],face2_vec[1],face2_vec[2]))
    outputfile.write("and plane(%f,%f,%f; %f,%f,%f)\n" \
                     % (face3_point[0],face3_point[1],face3_point[2],\
                        face3_vec[0],face3_vec[1],face3_vec[2]))
    outputfile.write("and plane(%f,%f,%f; %f,%f,%f);\n\n" \
                     % (face4_point[0],face4_point[1],face4_point[2],\
                        face4_vec[0],face4_vec[1],face4_vec[2]))

    print "Defining the outer pyramid:\n"
    outputfile.write("solid outerpyramid = plane(%f,%f,%f; %f,%f,%f)\n" \
                     % (bottom_point[0],bottom_point[1],bottom_point[2],\
                        bottom_vec[0],bottom_vec[1],bottom_vec[2]))
    outputfile.write("and plane(%f,%f,%f; %f,%f,%f)\n" \
                     % (face5_point[0],face5_point[1],face5_point[2],\
                        face5_vec[0],face5_vec[1],face5_vec[2]))
    outputfile.write("and plane(%f,%f,%f; %f,%f,%f)\n" \
                     % (face6_point[0],face6_point[1],face6_point[2],\
                        face6_vec[0],face6_vec[1],face6_vec[2]))
    outputfile.write("and plane(%f,%f,%f; %f,%f,%f)\n" \
                     % (face7_point[0],face7_point[1],face7_point[2],\
                        face7_vec[0],face7_vec[1],face7_vec[2]))
    outputfile.write("and plane(%f,%f,%f; %f,%f,%f);\n\n" \
                     % (face8_point[0],face8_point[1],face8_point[2],\
                        face8_vec[0],face8_vec[1],face8_vec[2]))

    print "Defining the magnetic domain:\n"
    outputfile.write("solid magneticdomain = outerpyramid and not innerpyramid -maxh=%f;\n" % elementlength)
    outputfile.write("tlo magneticdomain;\n")

    outputfile.close()

build_pyramid_shell(edgelength=2.0*h,height=h,width=w,elementlength=hmax)

