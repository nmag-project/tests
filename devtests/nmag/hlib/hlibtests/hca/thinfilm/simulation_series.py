#!/usr/bin/python
"""This python script uses the function thinfilm_simulation within the
file simulation.py in order to perform a parameter analysis of
hlib. Before the simulations can be run one has to create the
corresponding meshes by using the shell script setup.sh."""
import simulation

quadrature=[i for i in range(3,6)]
leafsize = [i*10 for i in range(1,5)]
polynome = [i for i in range(3,6)]
geo_criterion = [i*1.0 for i in range(1,5)]
accuracy = [10**i for i in range(-6,-2)]

#quadrature=[i for i in range(4,6)]
#leafsize = [i*5 for i in range(4,5)]
#polynome = [i for i in range(4,5)]
#geo_criterion = [i*0.5 for i in range(4,5)]
#accuracy = [10**i for i in range(-4,-3)]

for nfdeg in quadrature:
    for nmin in leafsize:
        for p in polynome:
            for eta in geo_criterion:
                for eps in accuracy:
                    simulation.iterate_hlib_simulations(nfdeg=3,nmin=20,p=4,eta=2.0,eps=0.0001,dirlist=['thinfilm50_50_5'])

print "Simulation has finished.\n"
