import pylab
import os
import math
import sys
import commands
import time
import re

#importing own scripts
import simulation

#some global definitions

#A file with the simulation results will be produced. For reading this file one needs to know
#which headings corresponding to which datatypes. Therefore the global lists intitems and
#floatitems are created. The advantage of this approach is that when changing the headings
#of the file one just has to change the lists accordantly.

intitems=['nfdeg','nmin','p','kmax']
floatitems=['eta','eps','eps_aca','dev-demag-th_(%)','dev-demag-ful_(%)','smx_(MB)','ful_(MB)','rk_(MB)',\
            'rate_(%)','time_(sec)','dt-ful_(sec)']


#these were initially items in the dictionary axisnames, but since
#they refer to parameters it does not really make sense to plot them
#on the axes. I just leave them here for a being able to use them
#later
#
#'nfdeg':'The quadrature q order',\
#'nmin':'The minimal leafsize of a clustertree',\
#'eta':'Geometrical admissibility parameter',\
#'eps':'Error bound eps for Singular Value Decomposition',\
#'eps_aca':'Error bound for adaptive cross apporximation',\
#'p':'The polynomial order of the kernel approximation',\
#'kmax':'Maximal rank of rk blocks',\


axisnames={'dev-demag-th_(%)':'Deviation from the theoretical value (in %)',\
           'dev-demag-ful_(%)':'Deviation from full BEM value (in %)',\
           'smx_(MB)':'Storage requirements for H-Matrix (in MB)',\
           'ful_(MB)':'Storage requirements for inadmissible leaves (in MB)',\
           'rk_(MB)':'Storage requirements for admissible leaves (in MB)',\
           'rate_(%)':'Compression rate of the H-Matrix (in %)',\
           'time_(sec)':'Time t needed to set up the supermatrix (in sec)',\
           'dt-ful_(sec)':'Time difference of full BEM setup. (in sec)'}


outputfilenames={'nfdeg':'nfdeg',\
                 'nmin':'nmin',\
                 'eta':'eta',\
                 'eps':'eps',\
                 'eps_aca':'eps_aca',\
                 'p':'p',\
                 'kmax':'kmax',\
                 'dev-demag-th_(%)':'DevDemagTh',\
                 'dev-demag-ful_(%)':'DevDemagFul',\
                 'smx_(MB)':'SizeSmx',\
                 'rk_(MB)':'SizeRk',\
                 'rate_(%)':'CompRate',\
                 'time_(sec)':'SetupTime',\
                 'dt-ful_(sec)':'TimeSave'}


#dictionary translating the simulation type into the list index in simulation.parameters
simulationtype={'aca':0, 'interpol':2, 'hca':3, 'bufacanormal':5,'hcanormal':6,'h2':7}

#some global default arguments, which are used within the function make_plot

deffilename = 'simulation.dat' #the default filename
defxaxis    = 'dev-demag-ful_(%)'
defyaxis    = 'rate_(%)'
defcolortag = 'eps'
defsymboltag = 'p'
deffixvalues = []
defxheading = 'None'
defyheading = 'None'



#regular expressions for testing whether a string is equivalent to an integer
integer=re.compile('^ *[-+]*[0-9]+ *$')
floattype=re.compile('^ *[-+]*[0-9]+\\.[0-9]* *$')

#regular expression for retrieving the number of nodes from the data file
nodenumber=re.compile('^ *[0-9]+,$')

def read_data(datafilename):
    """This function reads the simulation results from a file and returns a list
    of the headings of the file and a list with the corresponding data entries."""
    
    print "Entering read_data..."
    datafilename=str(datafilename)
    assert (os.path.exists(os.getcwd()+'/'+datafilename)==True),"The file %s does not exist.\n" % datafilename
    assert datafilename != '','No name for the datafile given!'
   
    typeconverter={}
    datafile=open(datafilename,'r')
    
    i=0 #introduced for distinguishing between the first, second and all other lines
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
            item=line.split()
            for j in range(len(item)):
                if nodenumber.match(item[j]):
                    surfacenodes=item[j].strip(',')
                    surfacenodes=int(surfacenodes)
                    if j == 0 or item[j-1]!='nodes:':
                        sys.stderr('Warning: The file does not seem to have the expected format.')
                    break
            i=2
        else:      #all other lines are just written into a list object
            item=line.split()
            for j in range(len(item)):
                datalist[j].append(typeconverter[j](item[j]))

    datafile.close()
    assert i!=0,'The datafile has been empty.'
    print "Leaving read_data..."
    return (headings,datalist,surfacenodes)



def split_list(list2split,index):
    """This function splits a list into sublists. This is done in the following way: First one
    condsiders the integer given by index and resorts the rows of list2split such that it consists
    of blocks with a constant the corresponding column into blocks
    of uniform value. For each block of constant value a corresponding sublist is created."""

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


def get_parameter_number(headinglist):
    """This functions takes as argument the list of headings in the simulation file.
    From that list it determines the number of parameters by comparing the list with
    the list parameters in the file simulation.py (Headings can be parameters or
    results. Parameters have to be adjusted before the simulation is started and thus
    determine the environment of the simulation.). The functions first returnvalue is
    the length and the second one the type of the simulation (aca, interpolation,hca)."""

    assert len(headinglist)>0,"The parameter list is obviously empty"
    for i in simulationtype.itervalues():
        length=len(simulation.parameters[i])
        counter=0
        countlist=list()
        for j in range(length):
            countlist.append(0)
        for item in headinglist:
            if item in simulation.parameters[i]:
                counter=counter+1
                index=simulation.parameters[i].index(item)
                countlist[index]=countlist[index]+1
                assert countlist[index]==1,"Obviously the list contains a heading twice."
            else:
                break
        
        if counter==length:
            break
        
    for j in countlist:
        assert j==1,"headinglist does not match a possible selection of parameters created within simulation.py"
    
    for j in simulationtype.iterkeys():
        if simulationtype[j]==i:
            break
    
    result=[]
    result.append(length)
    result.append(j)
    
    return tuple(result)
        

def get_parameter_ranges(headings=[],databody=[],filename='simulation.dat'):
    """This function computes the parameter ranges stored in a data file returned by the
    simulation. It returns three objects. The first two objects are
    just the returnvalues of the function get_parameter_number,
    i.e. the number of parameters of the simulation and an identifier
    of the simulation type. The second object is a list of lists. The first 
    element of each sublists contains the name of the parameter, and
    second entry is a list of values this particular parameter adopts
    in the data file. The arguments of the simulation are either the
    lists headings and databody, or the name of the data file. 
    Here the list headings contains the heading names, which have been obtained
    from the corresponding data file, and the list databody is a list of lists,
    which represent the columns of numerical data."""
    
    print "Entering get_parameter_ranges..."
    if (len(headings)==0 and len(databody)!=0) or (len(headings)!=0 and len(databody)==0):
        sys.stderr.write("Warning: Only headings or databody specified, try to open file.")
        
    if(len(headings)==0 or len(databody)==0):
        (headings,databody,surfacenodes)=read_data(filename)
        print "After calling read_data."
    else:
        assert len(headings)==len(databody)
    
    print "Before calling get_parameter_number..."
    (parameternumber,simulationtag) = get_parameter_number(headings)
    
    parameterrange=[]
    index=simulationtype[simulationtag]
    for i in range(parameternumber):
        parameterrange.append([])
        parameterrange[i].append(simulation.parameters[index][i])
        valueslist=[]
        for value in databody[i]:
            if value not in valueslist:
                valueslist.append(value)

        valueslist.sort()
        parameterrange[i].append(valueslist)
    
    result=[]
    result.append(parameternumber)
    result.append(simulationtag)
    result.append(parameterrange)
    print "Leaving get_parameter_ranges."
    return tuple(result)


def create_datafile(resulttype='smx_(MB)',simulationfiles=['oldsimulation_hacI.dat'],\
                    datafile='output.dat',eps=0.001,eps_aca=0.00001,nfdeg=2,p=3,\
                        eta=2.0,nmin=50,kmax=100):
    """This functions creates a new data file from a selection of files coming from
    simulations."""

    errorstring="The variable should contain one of the following strings:\n\n"
    k=1
    for item in axisnames.iterkeys():
        errorstring=errorstring+"%d: " % k
        errorstring=errorstring+item+"\n"

    assert resulttype in axisnames.iterkeys(),errorstring

    if type(eps)==str:
        assert floattype.match(eps),"String eps can not be converted to float."
        eps=float(eps)
    elif type(eps)==int:
        eps=float(eps)
    else:
        assert type(eps)==float,"Variable nfdeg is of invalid type."

    if type(eps_aca)==str:
        assert floattype.match(eps_aca),"String eps_aca can not be converted to float."
        eps_aca=float(eps_aca)
    elif type(eps_aca)==int:
        eps_aca=float(eps_aca)
    else:
        assert type(eps_aca)==float,"Variable eps_aca is of invalid type."

    if type(nfdeg)==str:
        assert integer.match(nfdeg),"String nfdeg can not be converted to integer."
        nfdeg=int(nfdeg)
    elif type(nfdeg)==float:
        testvar=nfdeg-1.0*int(nfdefg)
        assert testvar==0.0,"Float variable nfdeg can not be converted to integer."
        nfdeg=int(nfdeg),""
    else:
        assert type(nfdeg)==int,"Variable nfdeg is of invalid type."

    if type(p)==str:
        assert integer.match(p),"Variable p can not be converted to integer."
        p=int(p)
    elif type(p)==float:
        testvar=p-1.0*int(p)
        assert testvar==0.0,"Float p can not be converted to integer."
        p=int(p)
    else:
        assert type(p)==int,"Variable p is of invalid type."

    if type(eta)==str:
        assert floattype.match(eta),"String eta can not be converted to float. "
        eta=float(eta)
    elif type(eta)==int:
        eta=float(eta)
    else:
        assert type(eta)==float,"Variable eta is of invalid type."

    if type(nmin)==str:
        assert integer.match(nmin),"String nmin can not be converted to integer."
        nmin=int(nmin)
    elif type(nmin)==float:
        testvar=nmin-1.0*int(nmin)
        assert testvar==0.0,"Float nmin can not be converted to integer."
        nmin=int(nmin)
    else:
        assert type(nmin)==int,"Variable nmin is of invalid type."

    if type(kmax)==str:
        assert integer.match(kmax),"String kmax can not be converted to integer."
        kmax=int(kmax)
    elif type(kmax)==float:
        testvar=kmax-1.0*int(kmax)
        assert testvar==0.0,"Float kmax con not be converted to integer."
        kmax=int(kmax)
    else:
        assert type(kmax)==int,"Variable kmax is of invalid type."

    assert len(simulationfiles)>0,"There are no simulation files specified."
    surfacenodeslist=[]
    resultlist=[]

    for i in range(len(simulationfiles)):
        assert type(simulationfiles[i])==str,"Simulation files should be given as strings."
        assert os.path.exists(simulationfiles[i]),"File %s does not exist." % simulationfiles[i]
        
        (headings,datalist,surfacenodes)=read_data(simulationfiles[i])
        surfacenodeslist.append(surfacenodes)
        (parameternumber,simulationtag,parameterrange)=get_parameter_ranges(headings=headings,databody=datalist)
        if i==0:
            simureference=simulationtag
            simuindex=simulationtype[simureference]
            resultindex=headings.index(resulttype)
        else:
            assert simureference==simulationtag,"Files %s and %s correspond to different simulations."
        
        for j in range(len(simulation.parameters[simuindex])):
            paravalue=vars()[simulation.parameters[simuindex][j]]
            assert paravalue in parameterrange[j][1],"Invalid value for parameter %s." % simulation.parameters[simuindex][j]
            paraindex=headings.index(simulation.parameters[simuindex][j])
            sublists=split_list(datalist,paraindex)

            testvar=0
            for item in sublists:
                if paravalue==item[paraindex][0]:
                    datalist=item
                    testvar=1
                    break
            assert testvar==1,"The value for %s is not in the datafile." % simulation.parameters[simuindex][j]
        resultlist.append(datalist[resultindex][0])
    
    formatindex=resultindex-parameternumber
    assert len(surfacenodeslist)==len(resultlist),"The lists surfacenodeslist and resultlist have different dimensions."
    outputfile=open(datafile,"w")
    for k in range(len(surfacenodeslist)):
        outputstring="%d "+simulation.format_results[formatindex]+"\n"
        outputfile.write(outputstring % (surfacenodeslist[k],resultlist[k]))

    outputfile.close()
        
        
            

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

    assert type(filename)==str,"The variable filename should be of type string."
    assert type(xaxis)==str,"The variable xaxis should be of type string."
    assert type(yaxis)==str,"The variable yaxis should be of type string."
    assert type(colortag)==str,"The variable colortag should be of type string."
    assert type(symboltag)==str,"The variable symboltag should be of type string."
    for i in range(len(fixvalues)):
        assert type(fixvalues[i][0])==str,"In fixvalues: The first entry of the sublists should be of type string."
        if fixvalues[i][0] in intitems:
            if type(fixvalues[i][1])==str:
                assert integer.match(fixvalues[i][1]),"The string object is not equivalent to an integer."
                fixvalues[i][1]=int(fixvalues[i][1])
            else:
                assert type(fixvalues[i][1])==int,"A fixvalues entry is not convertible to int."
        elif fixvalues[i][0] in floatitems:
            if type(fixvalues[i][1])==str:
                assert floattype.match(fixvalues[i][1]),"The string object is not equivalent to a float."
                fixvalues[i][1]=float(fixvalues[i][1])
            else:
                assert type(fixvalues[i][1])==float,"A fixvalues entry is not convertible to float."
        else:
            sys.stderr.write("Entry in fixvalues neither in intitems nor in floatitems.")
            exit(1)
            
            
    assert type(xheading)==str,"Type of variable xheading should be of type string."
    assert type(yheading)==str,"Type of variable yheading should be of type string."
    
    datafile=read_data(filename)

    assert (xaxis in datafile[0] and yaxis in datafile[0] and colortag in datafile[0]\
            and symboltag in datafile[0]),"There is a unspecified argument given!"

    i1=datafile[0].index(symboltag)
    i2=datafile[0].index(colortag)
    
    (parameters,simulationtype)=get_parameter_number(datafile[0])
    assert (i1<parameters and i2<parameters),"colortag and symboltag should be parameters."
    
    j1=datafile[0].index(xaxis)
    j2=datafile[0].index(yaxis)

    print 'Setting the list fixvalues2'
    fixvalues2=[]  #creating a related list storing integer index and corresponding value
    if(len(fixvalues)!=0):
        for i in range(len(fixvalues)):
            assert len(fixvalues[i])==2,"A subarray of fixvalues is faulty."
            assert fixvalues[i][0]!=colortag and fixvalues[i][0]!=symboltag,"Plot parameter can not be fixed."
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
        if colortag=='eps' or colortag=='eps_aca':
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


def choose_parameter():
    print "This function lets you conveniently choose the arguments for"
    print "of the function make_scatter_plot.\n"
    
    global deffilename
    global defxaxis
    global defyaxis
    global defcolortag
    global defsymboltag
    global deffixvalues

    #Getting the filename
    filepath=''
    inputname=''
    firstrun=True
    while(os.path.exists(filepath)==False and os.path.exists(inputname)==False):
        if firstrun==False:
            os.system('clear')
            print "The entered filename does not correspond to an existing file,"
            print "please try once again!"
            time.sleep(2)
        else:
            firstrun=False
            os.system('clear')

        if (os.path.exists(os.getcwd()+'/'+deffilename)==True):
            inputname=raw_input('Please specify the name of the datafile from which the data\nof the simulation should be read!\nPress return for the default file name %s! ' % deffilename)
            if inputname=='':
                inputname=deffilename
        else:
            inputname=raw_input('Please specify the name of the datafile from which the \nsimulation data should be read! ')

        filepath=os.getcwd()+'/'+inputname


    if os.path.exists(filepath)==True and os.path.exists(inputname)==False:
        filename = filepath
    else:
        filename = inputname

    deffilename = filename

    #Getting the x-axis property
    xaxisstring='\nWhich property should be shown on the x-axis?\nPossible arguments are:\n\n'
    for keys in axisnames.iterkeys():
        newline = '%s\t->\t%s\n' % (keys,axisnames[keys])
        xaxisstring=xaxisstring+newline
    xaxisstring=xaxisstring+'\nPress return for the default name: %s\n' %  defxaxis
    
    xaxis=''
    firstrun=True
    while xaxis not in axisnames.iterkeys():
        if firstrun==False:
            os.system('clear')
            print "\nThe entered axisname is not valid,"
            print "please try once again!"
            time.sleep(2)
        else:
            firstrun=False
            os.system('clear')
        
        xaxis=raw_input(xaxisstring)
        if xaxis=='':
            xaxis=defxaxis

    defxaxis=xaxis

    #Getting the y-axis property
    yaxisstring='\nWhich property should be shown on the y-axis?\nPossible arguments are:\n\n'
    for keys in axisnames.iterkeys():
        if keys!=xaxis:
            newline = '%s\t->\t%s\n' % (keys,axisnames[keys])
            yaxisstring=yaxisstring+newline
    if defyaxis!=xaxis:
        yaxisstring=yaxisstring+'\nPress return for the default name: %s\n' %  defyaxis
    else:
        yaxisstring=yaxisstring+'\nEnter the appropriate key!\n'
    
    yaxis=''
    firstrun=True
    while yaxis not in axisnames.iterkeys():
        if firstrun==False:
            os.system('clear')
            print "\nThe entered axisname is not valid,"
            print "please try once again!"
            time.sleep(2)
            
        else:
            firstrun=False
            os.system('clear')
        
        yaxis=raw_input(yaxisstring)
        if yaxis=='' and defyaxis!=xaxis:
            yaxis=defyaxis

    defyaxis=yaxis

    #Getting the property colortag
    (parameternumber,simulationtag,parameterranges)=get_parameter_ranges(filename=filename)

    parameteroptions = [] #this definition is not really necessary
    for lists in parameterranges:
        parameteroptions.append(lists[0])
    
    colortagstring='Which parameter should be colorcoded in the plot?\nPossible parameters are:\n\n'
    for lists in parameterranges:
        colortagstring=colortagstring+'%s : ' % lists[0]
        item=[]
        for entries in lists[1]:
            item.append(str(entries))
        colortagstring=colortagstring+' %s' % item
        colortagstring=colortagstring+'\n'
    
    colortagstring=colortagstring+'\nPress return for the default name: %s\n' %  defcolortag
    colortag=''
    firstrun=True
    while colortag not in parameteroptions:
        if firstrun==False:
            os.system('clear')
            print "\nThe entered colortag is not valid,"
            print "please try once again!"
            time.sleep(2)
        else:
            firstrun=False
            os.system('clear')
        
        colortag=raw_input(colortagstring)
        if colortag=='':
            colortag=defcolortag

    defcolortag=colortag

    #Getting the property symboltag
    parameteroptions.remove(colortag) #deleting the entry already used in colortag

    for lists in parameterranges: #doing the same for parameterranges
        if lists[0]==colortag:
            deleteentry = lists
    parameterranges.remove(deleteentry)

    symboltagstring='Which parameter should be depicted by symbols in the plot?\nPossible parameters are:\n\n'
    for lists in parameterranges:
        symboltagstring=symboltagstring+'%s : ' % lists[0]
        item=[]
        for entries in lists[1]:
            item.append(str(entries))
        symboltagstring=symboltagstring+' %s' % item
        symboltagstring=symboltagstring+'\n'
    
    if defsymboltag==colortag:
        symboltagstring=symboltagstring+'\nPlease make one of the shown choices.\n'
    else:
        symboltagstring=symboltagstring+'\nPress return for the default name: %s\n' % defsymboltag

    symboltag=''
    firstrun=True
    while symboltag not in parameteroptions:
        if firstrun==False:
            os.system('clear')
            print "\nThe entered symboltag is not valid,"
            print "please try once again!"
            time.sleep(2)
        else:
            os.system('clear')
            firstrun=False
        
        symboltag=raw_input(symboltagstring)
        if symboltag=='' and defsymboltag!=colortag:
            symboltag=defsymboltag

    defsymboltag=symboltag
    
    #Getting the property fixvalues
    parameteroptions.remove(symboltag) #deleting the entry already used in symboltag

    for lists in parameterranges: #doing the same for parameterranges
        if lists[0]==symboltag:
            deleteentry = lists
    parameterranges.remove(deleteentry)
    fixvalues=[]

    while len(parameterranges) > 0:
        fixvaluesstring ="The following parameters can be kept fixed:\n"
        for lists in parameterranges:
            fixvaluesstring=fixvaluesstring+'%s : ' % lists[0]
            item=[]
            for entries in lists[1]:
                item.append(str(entries))
            fixvaluesstring=fixvaluesstring+' %s' % item
            fixvaluesstring=fixvaluesstring+'\n'

        fixvaluesstring=fixvaluesstring+"\nWhich parameter would you like to choose."
        fixvaluesstring=fixvaluesstring+"\nType exit if none!\n"
        os.system('clear')

        para2fix=raw_input(fixvaluesstring)

        if para2fix in parameteroptions:
            for lists in parameterranges:
                if lists[0]==para2fix:
                    while(True):
                        valuestring="Which value should the parameter %s have?\n" % para2fix
                        valuestring=valuestring+"Type \n"
                        for i in range(len(lists[1])):
                            valuestring=valuestring+"%d  for  %s\n" % (i,str(lists[1][i]))

                        index=raw_input(valuestring)
                        if integer.match(index):
                            index=int(index)
                            if index not in range(len(lists[1])):
                                os.system('clear')
                                print "The integer entered is not in the correct range, try again please?\n"
                                time.sleep(2)
                                pass
                            else:
                                tentativelist=[]
                                tentativelist.append(para2fix)
                                tentativelist.append(lists[1][index])
                                fixvalues.append(tentativelist)
                                break
                        else:
                            os.system('clear')
                            print "You did not enter an integer, please try again!\n"
                            time.sleep(2)
                    os.system('clear')
                    print "\nParameter %s set to %s.\n" % (tentativelist[0],str(tentativelist[1]))
                    parameteroptions.remove(para2fix) #deleting the entry just set
                    for lists in parameterranges: #doing the same for parameterranges
                        if lists[0]==para2fix:
                            deleteentry = lists
                            parameterranges.remove(deleteentry)
                    break
        elif para2fix=='exit':
            break
        else:
            os.system('clear')
            print "This parameter is not valid. Please try again!"
            time.sleep(2)
            pass
    
    #Getting a special labelling for the x-axis
    os.system('clear')
    xheadingstring="Do you want to enter a non-default labelling at the x-axis?\n"
    xheadingstring=xheadingstring+"If not, please just enter the return key or type No.\n"
    xheading=raw_input(xheadingstring)
    if xheading=='' or xheading=='no' or xheading=='No' or xheading=='NO':
        xheading=defxheading

    #Getting a special labelling for the y-axis
    os.system('clear')
    yheadingstring="Do you want to enter a non-default labelling at the y-axis?\n"
    yheadingstring=yheadingstring+"If not, please just enter the return key or type No.\n"
    yheading=raw_input(yheadingstring)
    if yheading=='' or yheading=='no' or yheading=='No' or yheading=='NO':
        yheading=defyheading

    
    print "That is the list fixvalues:"
    print fixvalues
    make_scatter_plot(filename=filename,xaxis=xaxis,yaxis=yaxis,colortag=colortag,\
                          symboltag=symboltag,fixvalues=fixvalues,xheading=xheading,\
                          yheading=yheading)
