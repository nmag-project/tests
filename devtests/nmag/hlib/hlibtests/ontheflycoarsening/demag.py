from math import sqrt,log,atan,pi

def demagfactor_prism(input_file,mode=2):
    """
    The function calculates the magnetometric demagnetising factor for
    a prism. The edge lengthes of the prism are read from a file. The
    first argument of the function is the file name. The second
    argument should be one of the three integers 0,1,2 and specifies
    whether the demagnetising factor with respect to the x,y or z
    direction has to be determined.
    """
    
    fileobj=open(input_file,"r")
    d=list()
    i=0
    for length in fileobj:
        assert i<3, "The file %s does not seem to have the correct length." % input_file
        d.append(float(length)/2.0)
        i=i+1
    
    fileobj.close()
    mode=int(mode)
    if mode==0:
        a = d[1]
        b = d[2]
        c = d[0]
    elif mode==1:
        a = d[2]
        b = d[0]
        c = d[1]
    else:
        a = d[0]
        b = d[1]
        c = d[2]

    a_2 = a**2
    b_2 = b**2
    c_2 = c**2
    length = sqrt(a_2+b_2+c_2)
    length_ab = sqrt(a_2+b_2)
    length_ac = sqrt(a_2+c_2)
    length_bc = sqrt(b_2+c_2)

    D = \
    (b_2-c_2)*log((length-a)/(length+a))/(2*b*c) +\
    (a_2-c_2)*log((length-b)/(length+b))/(2*a*c) +\
    b*log((length_ab+a)/(length_ab-a))/(2*c) +\
    a*log((length_ab+b)/(length_ab-b))/(2*c) +\
    c*log((length_bc-b)/(length_bc+b))/(2*a) +\
    c*log((length_ac-a)/(length_ac+a))/(2*b) + 2*atan(a*b/(c*length))\
    + (a*a_2+b*b_2-2*c*c_2)/(3*a*b*c) +\
    length*(a_2+b_2-2*c_2)/(3*a*b*c) + c*(length_ac+length_bc)/(a*b) -\
    (length_ab**3+length_bc**3+length_ac**3)/(3*a*b*c)
    
    return D/pi

    
