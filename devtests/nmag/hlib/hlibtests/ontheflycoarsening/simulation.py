import os
import re
import math
import time
import sys
import string
import commands

#own scripts
import demag

#some global definitions

#regular expression

dirbody=re.compile('^thinfilm[0-9][0-9].*')
meshfile=re.compile('^.*\\.nmesh\\.h5')
bemtime=re.compile('.*Populating BEM took.*')
timepattern=re.compile('[0-9]+\\.[0-9]+')


#initializing some paths

nsim=commands.getoutput('which nsim')
ncol=commands.getoutput('which ncol')  


#list of lists, that states which parameters a certain algorithm contains

parameters=[["nfdeg","nmin","eta","eps_aca","eps","kmax"],\
            ["nfdeg","nmin","eta","eps_aca","eps","kmax"],\
            ["nfdeg","nmin","eta","eps","p"],\
            ["nfdeg","nmin","eta","eps_aca","eps","p"],\
            ["nfdeg","nmin","eta","eps_aca","eps","p"],\
            ["nfdeg","nmin","eta","eps_aca","kmax"],\
	    ["nfdeg","nmin","eta","eps_aca","p"],\
            ["nfdeg","nmin","eta","eps","p"]]



#the lower and upper bound for each parameter is given within the corresponding dictionary

lowerbound={'algorithm':0,'nfdeg':1, 'nmin':1, 'eta':0.1,\
            'eps_aca':1e-10, 'eps':1e-10, 'p':1, 'kmax':1}

upperbound={'algorithm':7, 'nfdeg':10, 'nmin':300, 'eta':10.0,\
            'eps_aca':0.5, 'eps':0.5, 'p':10, 'kmax':300}


#a dictionary for asigning a certain outputfile name to each algorithm
outputfilename={0:'simulation_aca.dat', 1:'simulation_acap.dat', 2:'simulation_interpol.dat',\
                3:'simulation_hcaI.dat', 4:'simulation_hcaII.dat',\
		5:'simulation_bufacanormal.dat',6:'simulation_hcanormal.dat',\
		7:'simulation_h2.dat'}

#dictionary containing the file headings, such that the output is contained within nice tables
headingparameters={"nfdeg":" nfdeg ", "nmin":" nmin ", "eta":"  eta ", "eps_aca":\
                   "    eps_aca    ", "eps":"      eps      ", "p":"  p  ", "kmax":" kmax "}

headingresults = ["  dev-demag-th_(%) "," dev-demag-ful_(%) ","   smx_(MB) ","   ful_(MB) ",\
                  "    rk_(MB) ","  rate_(%) ","   time_(sec)","    dt-ful_(sec) "]

format_parameters = {"nfdeg":" %5d ", "nmin":" %4d ", "eta":" %4.1f ", "eps_aca":" %12.10f  ",\
                     "eps":" %12.10f  ", "p":" %3d ", "kmax":" %4d "}

format_results = ["%17.7f  ","%17.7f  ","%10.2f  ","%10.2f  ","%10.2f  ","%9.2f  ",\
                  "%11.2f  ","%15.2f  "]



#two dictionaries storing the data coming from the full BEM results

dictfulldemag={}
dictfulltime={}


#here we define the material parameters of permalloy

ms = 0.86e6
llg_damping = 0.5
exchange = 1.3e-11


def run_nsim_with_timing(command_string):
    """This function runs nsim with the command string, and extracts
    the time needed to setup the boundary element matrix."""

    command_string=str(command_string)
    print "Start run_nsim_with_timing with command:\n %s.\n" % command_string
    
    command_list=command_string.split()
    if command_list[0]!=nsim:
        sys.stderr.write('Warning: No nsim command used in run_nsim_with_timing.')

    os.system('ulimit -s 65536')
    output=commands.getoutput(command_string)

    loutput=string.split(output,'\n')

    check=0
    for line in loutput:
        if bemtime.match(line):
            timeline=line.split()
            break
        check=check+1

    assert check < len(loutput),"No time for populating the BEM has been found."
    
    check=0
    for item in timeline:
        if timepattern.match(item):
            delta_t=item
            check=1
            break

    assert check==1,"No time populating the BEM has been found."
    
    print "Leaving run_nsim_with_timing.\n"
    return float(delta_t)


def get_demagfactor(simname):
    """Given the name of the simulation this function extracts the
    demagnetisation energy from the corresponding nsim datafile and
    returns the demagnetisation factor."""

    simname=str(simname)
    print "Start get_demagfactor with simulation name %s.\n" % simname
    
    if(os.path.exists(os.getcwd()+'/'+simname+'_dat.ndt')==False):
        sys.stderr.write('Warning: Data file corresponding to %s\
        does not exist.\n' % simname)
        
    arguments=" "+simname+" E_demag"
    demagenergy=commands.getoutput(ncol+arguments)

    print "Leaving getdemagfactor.\n"
    return 1e7*float(demagenergy) / (2.0*math.pi*ms**2)



def fullbem_simulation(simufile,simuname,meshfilename='None',dicttag='Default'):
    """This function performs simulations using nsim but not HLib.
    The first two arguments are the name of the nsim script and the name of the
    simulation. The latter can be determined within the script file. The
    third (optional) argument is the name of the file containing the mesh. If
    unspecified the function will search the current directory for an appropriate
    file using the globally defined regular expression meshfile. This function does
    not return its results but writes them to the global dictionaries dictfulltime
    and dictfulldemag. The last argument determines the corresponding dictionary
    indices""" 

    print "Entering thinfilm_with_fullbem.\n"

    #if no meshfile is explicitly given one searches for it in the current directory
    if meshfilename=='None':
        ls=os.listdir("./")
        for entry in ls:
            if meshfile.match(entry):
                meshfilename=entry
                break

    assert(meshfilename != 'None'),"There is no meshfile in the current working directory."

    #running the simulation with full BEM
    arguments=simufile+" "+" "+meshfilename+" "+str(ms)+\
                   " "+str(exchange)+" "+" --clean"

    delta_t=run_nsim_with_timing(nsim+' '+arguments)

    #extracting the demagnetisation factor
    demagfactor = get_demagfactor(simuname)

    #append results to the global lists dictfulltime and dictfulldemag
    dictfulltime[str(dicttag)]  = delta_t
    dictfulldemag[str(dicttag)] = demagfactor
            
    print "Leaving thinfilm_with_fullbem.\n"


def iterate_fullbem_simulations(nsimfile=os.getcwd()+'/thinfilm_full.py',nsimname='thinfilm_full',dirlist=[],meshfilelist=[]):
    """This routine iterates over the function fullbem_simulation. The arguments
    nsimfile and nsimname are the nsim script and the simulation name (which is
    again defined within the script). The third argument is a list which contains the
    names of the directories where the simulations are to be executed. The fourth
    argument is a list which contains the names of the meshfiles. If those lists
    are not given, the routine searches the directory for the regular expression
    determined by dirbody.""" 

    print "Entering iterate_fullbem_simulations.\n"
    if len(dirlist)==0:
        assert len(meshfilelist)==0, "Directory list not given, but meshfilelist is."
        ls=os.listdir("./")
        for entry in ls:
            if dirbody.match(entry):
                os.chdir(entry)
                fullbem_simulation(simufile=nsimfile,simuname=simname,dicttag=entry)
                os.chdir('../')
    else:
        if len(meshfilelist)==0:
            for i in range(len(dirlist)):
                os.chdir(dirlist[i])
                fullbem_simulation(simufile=nsimfile,simuname=simname,dicttag=dirlist[i])
                os.chdir('../')
        else:
            assert len(meshfilelist)==len(dirlist),"The lists meshfilelist and dirlist have different dimensions."
            for i in range(len(dirlist)):
                os.chdir(dirlist[i])
                fullbem_simulation(simufile=nsimfile,simuname=simname,meshfilename=meshfilelist[i],dicttag=dirlist[i])
                os.chdir('../')

    print "Leaving iterate_fullbem_simulations.\n"



def read_simulation_data(filename='memory_info.dat'):
    """This function reads from a file (its name should be 'memory_info.dat'),
    containing the information:
    1st line: The number of surface nodes of the mesh (integer)
    2nd line: The number of bytes needed to store a double precision number (integer)
    3rd line: Total amount of storage for the H-Matrix in Megabyte (double)
    4th line: Total amount of storage for the inadmissible leaves in Magabyte (double)
    5th line: Total amount of storage for the admissible leaves in Megabyte (double)
    """
    memory_output = open(filename,"r")
    
    fullbem_data= list()
    memory_data = list()
    
    i=0
    for entries in memory_output:
        assert i<5, "There are too many entries in %s." % filename
        if i<2:
            fullbem_data.append(int(entries))
        else:
            memory_data.append(float(entries))
        i=i+1
            
    memory_output.close()
    assert i==5, "Obviously there are too few entries within %s." % filename

    return (fullbem_data,memory_data)



def write_to_file(algorithm,nfdeg,nmin,eta,eps_aca,eps,p,kmax,timing,demagf,time_full,demag_full):

    algorithm=int(algorithm)
    outputfile = os.getcwd()+'/'+outputfilename[algorithm]
    (fullbem_data,memory_data) = read_simulation_data()
    
    if os.path.exists(outputfile)==False:
        simu_output = open(outputfilename[algorithm],"w")
        
        headings = []  #the headings over all the columns are created
        for entry in parameters[algorithm]:
            headings.append(headingparameters[entry])
        headings.extend(headingresults)
        formatstring=str()
        for entry in headings:
            formatstring=formatstring+"%s "
        formatstring=formatstring+"\n"
        
        headings=tuple(headings)
        simu_output.write(formatstring % headings)

        simu_output.write("number of surface nodes: %9d,\t full bem storage %12.2f (MB)\n" %\
                                  (fullbem_data[0],1.0*fullbem_data[0]**2*\
                                   fullbem_data[1]/1000000.0))

    else:
        simu_output = open(outputfilename[algorithm],"a")



    rate = 100000000.0*memory_data[0]/(fullbem_data[1]*fullbem_data[0]**2)

    demag_theo = demag.demagfactor_prism("dimensions.txt") #theoretical value of demag factor
    

    formatstring = str() #here the columns are created
    for entry in parameters[algorithm]:
        formatstring = formatstring + format_parameters[entry]
    for entry in format_results:
        formatstring = formatstring + entry
    formatstring = formatstring + "\n"

    variables = []
    for entry in parameters[algorithm]:
        variables.append(vars()[entry])

    
    assert demag_theo!=0.0,"demag_theo should not be zero since it appears in the denominator."
    assert demag_full!=0.0,"demag_full should not be zero since it appears in the denominator."

    variables.extend([100.0*(demagf-demag_theo)/demag_theo,\
                      100.0*(demagf-demag_full)/demag_full, memory_data[0], memory_data[1],\
                      memory_data[2],rate,timing,time_full-timing])

    variables = tuple(variables)
    simu_output.write(formatstring % variables)
                                  
    simu_output.close()
    

def hlib_simulation(hlibsimufile,hlibsimuname,fullsimufile,fullsimuname,meshfilename='None',fulldicttag='Default',algorithm=4,nfdeg=2,nmin=50,eta=20,eps_aca=0.00001,eps=0.00001,p=3,kmax=50):
    """This function runs a simulation using Nsim and HLib. The HLib parameters are given
    by the function arguments algorithm, nfdeg, nmin, eta, eps_aca, eps, p, and kmax,
    the meshfile by the argument meshfilename, the nsim script file by hlibsimufile and the
    simulation name (which is specified in the script file) by the hlibsimuname. For
    comparing the results with those obtained by an equivalent simulation using the full BEM,
    the function fullbem_simulation is called. This latter functions stores the time needed
    to set up the full boundary element matrix and the result for the demagnetising factor
    in the globally defined dictionaries dictfulltime and dictfulldemag respectively.
    The arguments fullsimufile and fullsimuname again specify the corresponding script file
    and the simulation name. By calling the function write_to_file the results of the
    simulation are written (or appended) to a file simulation.dat."""

    print "Entering function hlib_simulation...\n"

    #first: tests whether parameters are in the reasonable range
    algorithm = int(algorithm)
    assert (algorithm>=lowerbound['algorithm'] and algorithm<=upperbound['algorithm']),\
           "The parameter algorithm is not in the range [%d,%d]."\
           % (lowerbound['algorithm'],upperbound['algorithm'])

    for entry in parameters[algorithm]:
        assert (vars()[entry]>=lowerbound[entry] and vars()[entry]<=upperbound[entry]),\
               "Variable %s is out of bounds." % entry

    hlibsimufile=str(hlibsimufile)
    hlibsimuname=str(hlibsimuname)
    fullsimufile=str(fullsimufile)
    fullsimuname=str(fullsimuname)
    meshfilename=str(meshfilename)
    fulldicttag=str(fulldicttag)


    #search for meshfile in current directory if no filename is specified
    if (meshfilename=='None'):
        ls=os.listdir("./")
        for entry in ls:
            if meshfile.match(entry):
                meshfilename=entry
                break

    assert(meshfilename != 'None'),"There is no meshfile in the current working directory."


    if (fulldicttag not in dictfulldemag or fulldicttag not in dictfulltime):
        fullbem_simulation(simufile=fullsimufile,simuname=fullsimuname,\
                           meshfilename=meshfilename,dicttag=fulldicttag)


    time_full  = dictfulltime[fulldicttag]
    demag_full = dictfulldemag[fulldicttag]
    
    arguments=hlibsimufile+" "+" "+meshfilename+" "+str(ms)+\
               " "+str(exchange)+" "+str(algorithm)+" "+\
               str(nfdeg)+" "+str(nmin)+" "+str(eta)+" "+\
               str(eps_aca)+" "+str(eps)+" "+str(p)+" "+\
               str(kmax)+" --clean"

    timing=run_nsim_with_timing(nsim+' '+arguments) #run simulation + get time for BEM setup
        
    demagf = get_demagfactor(hlibsimuname) #computation of the demagnetisation factor

    write_to_file(algorithm=algorithm,nfdeg=nfdeg,nmin=nmin,eta=eta,\
                  eps_aca=eps_aca,eps=eps,p=p,kmax=kmax,timing=timing,\
                  demagf=demagf,time_full=time_full,demag_full=demag_full)
            
    
            

def iterate_hlib_simulations(hlibsimufile=os.getcwd()+'/thinfilm.py',hlibsimuname='thinfilm',\
                             fullsimufile=os.getcwd()+'/thinfilm_full.py',\
                             fullsimuname='thinfilm_full',dirlist=[],meshfilelist=[],\
                             algorithm=4,nfdeg=2,nmin=50,eta=20,eps_aca=0.00001,\
                             eps=0.00001,p=3,kmax=50):
    """This function does performs simulations with nsim and hlib. The nsim
    script is the thinfilm.py file. Then the function looks for directories
    of the form thinfilmx_y_z, where x, y and z are the film dimensions in
    the corresponding cartesian direction. The folders first have to
    be set up by using the shell script setup.sh. Currently the
    function is used by the python script simulation_series.py."""    

    print "Entering function iterate_hlib_simulations ...\n"

    if (len(dirlist)==0):
        ls=os.listdir("./")
        for entry in ls:
            if dirbody.match(entry):
                os.chdir(entry)
                hlib_simulation(hlibsimufile=hlibsimufile,hlibsimuname=hlibsimuname,\
                                fullsimufile=fullsimufile,fullsimuname=fullsimuname,\
                                meshfilename='None',fulldicttag=entry,algorithm=algorithm,\
                                nfdeg=nfdeg,nmin=nmin,eta=eta,eps_aca=eps_aca,eps=eps,\
                                p=p,kmax=kmax)
                os.chdir('../')
    else:
        if len(meshfilelist)==0:
            for i in range(len(dirlist)):
                os.chdir(dirlist[i])
                hlib_simulation(hlibsimufile=hlibsimufile,hlibsimuname=hlibsimuname,\
                                fullsimufile=fullsimufile,fullsimuname=fullsimuname,\
                                meshfilename='None',fulldicttag=dirlist[i],algorithm=algorithm,\
                                nfdeg=nfdeg,nmin=nmin,eta=eta,eps_aca=eps_aca,eps=eps,\
                                p=p,kmax=kmax)
                os.chdir('../')
        else:
            assert len(meshfilelist)==len(dirlist),\
                   "The lists meshfilelist and dirlist have different dimensions."
            for i in range(len(dirlist)):
                os.chdir(dirlist[i])
                hlib_simulation(hlibsimufile=hlibsimufile,hlibsimuname=hlibsimuname,\
                                fullsimufile=fullsimufile,fullsimuname=fullsimuname,\
                                meshfilename=meshfilelist[i],fulldicttag=dirlist[i],\
                                algorithm=algorithm,nfdeg=nfdeg,nmin=nmin,eta=eta,\
                                eps_aca=eps_aca,eps=eps,p=p,kmax=kmax)
                os.chdir('../')

    print "Leaving function iterate_hlib_simulations ...\n"



