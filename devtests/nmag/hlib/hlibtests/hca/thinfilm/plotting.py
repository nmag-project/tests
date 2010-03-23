import pylab
import os
import math
import sys
import commands

#some global definitions

#depending on which method (HCA,ACA) one uses the number of parameter might differ

parameters = 5


#A file with the simulation results will be produced. For reading this file one needs to know
#which headings corresponding to which datatypes. Therefore the global lists intitems and
#floatitems are created. The advantage of this approach is that when changing the headings
#of the file one just has to change the lists accordantly.

intitems=['nfdeg','nmin','p']
floatitems=['eta','eps','dev-demag-th_(%)','dev-demag-ful_(%)','smx_(MB)','ful_(MB)','rk_(MB)',\
            'rate_(%)','time_(sec)','dt-ful_(sec)']

axisnames={'nfdeg':'The quadrature q order',\
           'nmin':'The minimal leafsize of a clustertree',\
           'p':'The polynomial order of the kernel approximation',\
           'eta':'Geometrical admissibility parameter',\
           'eps':'Error bound eps for ACA',\
           'dev-demag-th_(%)':'Deviation from the theoretical value (in %)',\
           'dev-demag-ful_(%)':'Deviation from full BEM value (in %)',\
           'smx_(MB)':'Storage requirements for H-Matrix (in MB)',\
           'ful_(MB)':'Storage requirements for inadmissible leaves (in MB)',\
           'rk_(MB)':'Storage requirements for admissible leaves (in MB)',\
           'rate_(%)':'Compression rate of the H-Matrix (in %)',\
           'time_(sec)':'Time t needed to set up the supermatrix (in sec)',\
           'dt-ful_(sec)':'Time difference of full BEM setup. (in sec)'}


outputfilenames={'nfdeg':'nfdeg',\
                 'nmin':'nmin',\
                 'p':'p',\
                 'eta':'eta',\
                 'eps':'eps',\
                 'dev-demag-th_(%)':'DevDemagTh',\
                 'dev-demag-ful_(%)':'DevDemagFul',\
                 'smx_(MB)':'SizeSmx',\
                 'rk_(MB)':'SizeRk',\
                 'rate_(%)':'CompRate',\
                 'time_(sec)':'SetupTime',\
                 'dt-ful_(sec)':'TimeSave'}


def read_data(datafilename):
    """This function reads the simulation results from a file and returns a list
    of the headings of the file and a list with the corresponding data entries."""
    
    datafilename=str(datafilename)
    assert (os.path.exists(os.getcwd()+'/'+datafilename)==True),"The file %s does not exist.\n" % datafilename

    typeconverter={}
    datafile=open(datafilename,'r')
    
    i=0
    for line in datafile:
        if i==0:
            item=line.split()
            headings=item
            for j in range(len(item)):
                if item[j] in intitems:
                    typeconverter[j]=lambda x: int(x)
                elif item[j] in floatitems:
                    typeconverter[j]=lambda x: float(x)
                else:
                    sys.stderr.write('read_data_function: One data item was not recognised\n')

            datalist=list()
            for k in headings:
                datalist.append([])
            i=1
        elif i==1: #the second line of the file is currently not used
            i=2 
        else:      #all other lines are just written into a list object
            item=line.split()
            for j in range(len(item)):
                datalist[j].append(typeconverter[j](item[j]))

    
    datafile.close()
    return (headings,datalist)



def split_list(list2split,index):
    """This function splits a list into sublists. This is done in the following way: First one
    condsiders the integer given by index and sorts the corresponding column into blocks
    of uniform value."""

    assert (index > -1 and index < len(list2split)),"Index is out of range."
    
    testlist=list()
    testlist.append(list2split[index][0])
    
    for i in range(1,len(list2split[index])):
        if list2split[index][i] not in testlist:
            testlist.append(list2split[index][i])

    testlist.sort()
    accumulator=[]
    for i in range(len(testlist)):
        sublist=[]
        for j in range(len(list2split)):
            sublist.append([])
        for k in range(len(list2split[index])):
            if list2split[index][k]==testlist[i]:
                for l in range(len(list2split)):
                    sublist[l].append(list2split[l][k])
        accumulator.append(sublist)

    return accumulator



def make_scatter_plot(filename='simulation.dat',xaxis='dev-demag-ful_(%)',yaxis='rate_(%)',colortag='eps',symboltag='p',fixvalues=[],xheading='None',yheading='None'):
    """This functions makes a two-dimensional scatter plot. x and y axis are determined
    by the variables xaxis and yaxis. The variable colortag specifies the parameter, which
    determines the color of the scattered objects. Accordantly the variable symboltag specifies
    the parameter whose value varies the shape of the scattered objects.The list fixvalues has
    be a list of two-dimensional list. The first value of a two-dimensional sublists is the name
    of a parameter and the second entry specifies a value to which the parameter will be set
    in the plot. Finally one can state non-standard axis titles by giving corresponding strings
    to the variables xheading and yheading."""
    

    symbols=['o','s','^','>','v','<','h','p','d','8']
    symbolnames=['circles: ','squares: ','triangles up: ','triangles right: ',\
                 'triangles down: ','triangles left: ','hexagons: ','pentagrams: ',\
                 'diamond: ','octagon: ']
    
    datafile=read_data(filename)

    assert (xaxis in datafile[0] and yaxis in datafile[0] and colortag in datafile[0]\
            and symboltag in datafile[0]),"There is a unspecified argument given!"

    i1=datafile[0].index(symboltag)
    i2=datafile[0].index(colortag)

    assert (i1<parameters and i2<parameters),"colortag and symboltag should be parameters."
    
    j1=datafile[0].index(xaxis)
    j2=datafile[0].index(yaxis)

    print 'Setting the list fixvalues2'
    fixvalues2=[]  #creating a related list storing integer index and corresponding value
    if(len(fixvalues)!=0):
        for i in range(len(fixvalues)):
            assert len(fixvalues[i])==2,"A subarray of fixvalues is faulty."
            assert fixvalues[i][0]!=colortag and fixvalues[i][0]!=symboltag,"Plot parameter can not be fixed."
            assert fixvalues[i][0] in ['nfdeg','p','nmin','eps','eta'],"Unidentified name in fixvalues"
            if fixvalues[i][0] in intitems:
                item=list()
                item.append(datafile[0].index(fixvalues[i][0]))
                item.append(int(fixvalues[i][1]))
                fixvalues2.append(item)
            elif fixvalues[i][0] in floatitems:
                item=list()
                item.append(datafile[0].index(fixvalues[i][0]))
                item.append(float(fixvalues[i][1]))
                fixvalues2.append(item)
            else:
                sys.stderr.write('Fixvalue argument neither in intitems nor in floatitems list.\n')

    print 'Setting the array reduced_data'
    reduced_data=[]
    for i in range(len(datafile[1])):
        reduced_data.append([])    
    
    for i in range(len(datafile[1][0])):
        additem=True
        for j in range(len(fixvalues2)):
            if(datafile[1][fixvalues2[j][0]][i] != fixvalues2[j][1]):
                additem=False

        if additem==True:
            for j in range(len(reduced_data)):
                reduced_data[j].append(datafile[1][j][i])

    
    
    print "Splitting the list read from the datafile."
    plotdata=[reduced_data[i1],reduced_data[i2],reduced_data[j1],reduced_data[j2]]
    plotlist=split_list(plotdata,0) #splitting the list into sublists with constant parameter 0

    i=0
    cbrange=[] #the range of the colorbar
    legendlist=[] #will store the legend
    print "Now we are entering the loop for the creation of different scatter symbols.\n"
    for plots in plotlist:
        print 'Begin turn in loop ...'
        if colortag=='eps':
            for j in range(len(plots[1])):
                plots[1][j]=math.log10(plots[1][j])

        print 'After assignment for colortag=eps'
        for item in plots[1]:
            if item not in cbrange:
                cbrange.append(item)

        print 'After checking the whether the cbrange has to be extended.'
        pylab.scatter(plots[2],plots[3],s=50,c=plots[1],marker=symbols[i])
        print 'After using pylab.scatter.'
        legendentry=symbolnames[i]+symboltag+" = "+str(plots[0][0])
        legendlist.append(legendentry)
        print 'After extending the legendlist object.'
        i=i+1

    print 'Leaving the loop...'
    if (xheading=='None'): #Labelling the x axis
        pylab.xlabel(axisnames[xaxis],fontsize=15)
    else:
        pylab.xlabel(xheading,fontsize=15)

    if (yheading=='None'): #Labelling the y axis
        pylab.ylabel(axisnames[yaxis],fontsize=15)
    else:
        pylab.ylabel(yheading,fontsize=15)

    cbrange.sort()
    pylab.colorbar(extend='neither',spacing='uniform',ticks=cbrange)
    pylab.legend(tuple(legendlist),loc='upper left')

    print('Building the titlename...')
    titlename='Scatter plot (colors: '+colortag+' symbols: '+symboltag+')'
    for i in range(len(fixvalues)):
        titlename=titlename+'  '+fixvalues[i][0]+': '+str(fixvalues[i][1])
    pylab.title(titlename)
    
    figurename=outputfilenames[yaxis]+'_vs_'+outputfilenames[xaxis]+'_param_'+colortag+'_'+symboltag
    if len(fixvalues)>0:
        figurename=figurename+'_fixed:'
        for i in range(len(fixvalues)):
            figurename=figurename+'_'+fixvalues[i][0]+str(fixvalues[i][1])

    figurename=figurename+'.eps'
    pylab.savefig(figurename)
    pylab.show()

