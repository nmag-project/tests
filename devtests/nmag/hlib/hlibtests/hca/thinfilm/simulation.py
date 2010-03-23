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
starttime=re.compile('^.*dense_matrices start$')
endtime=re.compile('^.*dense_matrices end$')
timepattern=re.compile('^T=.*')


#initializing some paths

nsim=commands.getoutput('which nsim')
ncol=commands.getoutput('which ncol')  


#two dictionaries storing the data coming from the full BEM results

dictfulldemag={}
dictfulltime={}


#here we define the material parameters of permalloy

ms = 0.86e6
llg_damping = 0.5
exchange = 1.3e-11


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


def run_nsim_with_timing(command_string):
    """This function runs nsim with the command string, and extracts
    the time needed to setup the boundary element matrix."""

    command_string=str(command_string)
    print "Start run_nsim_with_timing with command:\n %s.\n" % command_string
    
    command_list=command_string.split()
    if command_list[0]!=nsim:
        sys.stderr.write('Warning: No nsim command used in run_nsim_with_timing.')
    
    output=commands.getoutput(command_string)

    loutput=string.split(output,'\n')
        
    for line in loutput:
        if starttime.match(line):
            tstart=line.split()
        elif endtime.match(line):
            tend=line.split()

    check=0
    for item in tstart:
        if timepattern.match(item):
            tstart=item
            check=1
            break

    assert check==1,"No time pattern for start time has been found."

    check=0
    for item in tend:
        if timepattern.match(item):
            tend=item
            check=1
            break

    assert check==1,"No time pattern for end time has been found."
            
    tstart=tstart.split('=')
    tend=tend.split('=')
    print "Leaving run_nsim_with_timing.\n"
    return float(tend[1])-float(tstart[1])


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


def hlib_simulation(hlibsimufile,hlibsimuname,fullsimufile,fullsimuname,meshfilename='None',fulldicttag='Default',nfdeg=3,nmin=20,p=4,eta=2.0,eps=0.0001):
    """This function runs a simulation using Nsim and HLib. The HLib parameters are given
    by the function arguments nfdeg, nmin, p, eta, and eps, the meshfile by the argument
    meshfilename, the nsim script file by hlibsimufile and the simulation name (which is
    specified in the script file) by the hlibsimuname. For comparing the results with those
    obtained by an equivalent simulation using the full BEM, the function fullbem_simulation
    is called. This latter functions stores the time needed to set up the full boundary
    element matrix and the result for the demagnetising factor in the globally defined
    dictionaries dictfulltime and dictfulldemag respectively. The arguments fullsimufile
    and fullsimuname again specifie the corresponding script file and the simulation name.
    The results of the simulation are written (or appended) to a file simulation.dat."""    

    print "Entering function hlib_simulation...\n"

    #test of the arguments of the function:
    nfdeg = int(nfdeg)
    assert (nfdeg>0 and nfdeg<20), "nfdeg does not have a reasonable value!"
    
    nmin = int(nmin)
    assert (nmin>0 and nmin<200), "nmin is out of range!"
    
    p = int(p)
    assert (p>-1 and p<20), "Polynomial order out of range!"
    
    eta = float(eta)
    assert (eta>0.1 and eta<10.0), "eta out of  range!" 
    
    eps = float(eps)
    assert (eps>1e-10 and eps<0.5), "eps out of range"

    hlibsimufile=str(hlibsimufile)
    hlibsimuname=str(hlibsimuname)
    fullsimufile=str(fullsimufile)
    fullsimuname=str(fullsimuname)
    meshfilename=str(meshfilename)
    fulldicttag=str(fulldicttag)


    #if no meshfilename is specified, the routine searches for one in the current working directory
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


    demag_full = dictfulldemag[fulldicttag]
    time_full  = dictfulltime[fulldicttag]
    
    arguments=hlibsimufile+" "+" "+meshfilename+" "+str(ms)+\
               " "+str(exchange)+" "+str(nfdeg)+" "+\
               str(nmin)+" "+str(p)+" "+str(eta)+" "+\
               str(eps)+" --clean"

    #running the simulation and measuring the needed to set up the supermatrix
    timing=run_nsim_with_timing(nsim+' '+arguments)
        
    #computation of the demagnetisation factor
    demagf = get_demagfactor(hlibsimuname)
            
    #computation of the theoretical demagnetisation factor, requires a file dimensions text,
    #which has been created during the run of setup.sh
    demagf_theo = demag.demagfactor_prism("dimensions.txt")
            
    #The file memory_info.dat contains the following entries:
    # 1.line: The number of surface nodes
    # 2.line: The number of bytes needed to store a double precision number
    # 3.line: Total amount of storage for the H-Matrix (in Megabyte)
    # 4.line: Amount of storage for the inadmissible leaves (in Megabyte)
    # 5.line: Amount of storage for the admissible leaves (in Megabyte)

    memory_output = open('memory_info.dat',"r")
    fullbem_data= list()
    memory_data = list()
    i=0
    for entries in memory_output:
        assert i<5, "There are too many entries in memory_info.dat."
        if i<2:
            fullbem_data.append(int(entries))
        else:
            memory_data.append(float(entries))
        i=i+1
            
    memory_output.close()

    #rate is the compression rate
    rate = memory_data[0]*100000000.0/fullbem_data[0]**2/fullbem_data[1]
            
    outputfile = os.getcwd()+"/simulation.dat"
    if os.path.exists(outputfile)==False:
        simu_output = open("simulation.dat","w")
        simu_output.write("%s %s %s %s %s %s %s %s %s %s %s %s %s\n" %\
                          (" nfdeg "," nmin ","  p  ","  eta ",\
                           "       eps","  dev-demag-th_(%) ",\
                           "dev-demag-ful_(%)","  smx_(MB)","   ful_(MB)",\
                           "    rk_(MB)","  rate_(%) ","   time_(sec)",\
                           "    dt-ful_(sec) "))

        simu_output.write("number of surface nodes: %9d,\t full bem storage %12.2f (MB)\n" %\
                                  (fullbem_data[0],1.0*fullbem_data[0]**2*\
                                   fullbem_data[1]/1000000.0))
                
    else:
        simu_output = open("simulation.dat","a")


    simu_output.write("%4d %7d %5d %7.2f %14.9f %14.7f %16.7f %11.2f %11.2f %11.2f %10.2f %14.5f %15.5f\n"% 
                      (nfdeg,nmin,p,eta,eps,\
                       (demagf-demagf_theo)*100/demagf_theo,\
                       (demagf-demag_full)*100/demag_full,\
                       memory_data[0],memory_data[1],memory_data[2],\
                       rate,timing,time_full-timing))
            
    simu_output.close()
            

def iterate_hlib_simulations(hlibsimufile=os.getcwd()+'/thinfilm.py',hlibsimuname='thinfilm',\
                             fullsimufile=os.getcwd()+'/thinfilm_full.py',\
                             fullsimuname='thinfilm_full',dirlist=[],meshfilelist=[],\
                             nfdeg=3,nmin=20,p=4,eta=2.0,eps=0.0001):
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
                                meshfilename='None',fulldicttag=entry,nfdeg=nfdeg,nmin=nmin,\
                                p=p,eta=eta,eps=eps)
                os.chdir('../')
    else:
        if len(meshfilelist)==0:
            for i in range(len(dirlist)):
                os.chdir(dirlist[i])
                hlib_simulation(hlibsimufile=hlibsimufile,hlibsimuname=hlibsimuname,\
                                fullsimufile=fullsimufile,fullsimuname=fullsimuname,\
                                meshfilename='None',fulldicttag=dirlist[i],nfdeg=nfdeg,\
                                nmin=nmin,p=p,eta=eta,eps=eps)
                os.chdir('../')
        else:
            assert len(meshfilelist)==len(dirlist),\
                   "The lists meshfilelist and dirlist have different dimensions."
            for i in range(len(dirlist)):
                os.chdir(dirlist[i])
                hlib_simulation(hlibsimufile=hlibsimufile,hlibsimuname=hlibsimuname,\
                                fullsimufile=fullsimufile,fullsimuname=fullsimuname,\
                                meshfilename=meshfilelist[i],fulldicttag=dirlist[i],\
                                nfdeg=nfdeg,nmin=nmin,p=p,eta=eta,eps=eps)
                os.chdir('../')

    print "Leaving function iterate_hlib_simulations ...\n"



