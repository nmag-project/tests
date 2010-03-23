#!/usr/bin/python
"""This python script uses the function thinfilm_simulation within the
file simulation.py in order to perform a parameter analysis of
hlib. Before the simulations can be run one has to create the
corresponding meshes by using the shell script setup.sh."""
import simulation


directories=['thinfilm50_50_5']

algorithmlist = [i for i in range(7,8)]
nfdeglist = [i for i in range(3,4)]
nminlist = [10*i for i in range(3,4)]
etalist = [1.0*i for i in range(2,3)]
eps_acalist = [10**i for i in range(-3,-2)]
epslist = [10**i for i in range(-2,-1)]
plist = [i for i in range(5,6)]
kmaxlist = [100*i for i in range(1,2)]


for algorithm in algorithmlist:
    for nfdeg in nfdeglist:
        for nmin in nminlist:
            for eta in etalist:
                for eps_aca in eps_acalist:
                    for eps in epslist:
                        for p in plist:
                            for kmax in kmaxlist:
                                simulation.iterate_hlib_simulations(algorithm=algorithm,\
                                                                    nfdeg=nfdeg,nmin=nmin,\
                                                                    eta=eta,eps_aca=eps_aca,\
                                                                    eps=eps,p=p,kmax=kmax,\
                                                                    dirlist=directories)
                                if(algorithm>1 and algorithm!=5):
                                    break
                            if(algorithm<=1 or algorithm==5):
                                break
                        if(algorithm==5 or algorithm==6):
                            break
                    if(algorithm==2 or algorithm==7):
                        break


print "Simulation has finished..."
