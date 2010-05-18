import nmag
from nmag import SI, every, at
from random import random
from scipy.optimize import bisect
import math

#definition of the vacuum permeability
mu0 = SI(4.0*math.pi*1.0e-7,"N/A^2")

#setting of material parameters
Ms = SI(1.0e6, "A/m")
A  = SI(13.0e-12, "J/m")

#magnetostatic energy density
Km = 1.0 / 2.0 * mu0 * Ms**2

#computing uniaxial anisotropy for standard problem 3 
K1 = 0.1 * Km
easy_axis = [ 0, 0, 1]

#defining exchange length
lexch = SI(math.sqrt(A.value/Km.value), "m")
#lexch = (A/Km)**0.5

#initial configuration for flower state computation
flower_init = [ 0, 0, 1]


def initial_vortex((x,y,z)):
    """Creating a vortex-like initial magnetisation with the core pointing in x
    direction. The analytic expression for the vortex has been taken from

    Guslienko et al. "Field evolution of magnetic vortex state in ferromagnetic 
    disks", APPLIED PHYSICS LETTERS, Volume 78, Number 24

    The size of the vortex core is assumed to be twice as large as the diameter
    of the vortex core.

    """

    global lexch

    x = 1e9*x
    y = 1e9*y
    z = 1e9*z

    b = 2*lexch.value
    #b = 2*float(lexch/SI('m'))
    rho = x**2 + y**2

    phi = math.atan2(z,x)
    m_phi = math.sin(2 * math.atan(rho/b))

    mx = math.sqrt(1.0-m_phi**2)
    my =  m_phi * math.cos(phi)
    mz = -m_phi * math.sin(phi)
    
    magnitude = math.sqrt(mx*mx+my*my+mz*mz)
    result = [mx/magnitude,my/magnitude,mz/magnitude]

    return result



def energy_flowerstate(length):
    global Ms
    global A
    global K1
    global easy_axis
    global lexch
    global flower_init

    edgelength = lexch*length

    mat_Py = nmag.MagMaterial(name="Mat",
                              Ms=Ms,
                              exchange_coupling=A,
                              anisotropy=nmag.uniaxial_anisotropy(axis=easy_axis, 
                                                                  K1=K1),
                              llg_damping=1.0
                              )

    simname = "cube_flower"+str(length)
    simname = "cube_flower%020.15f" % length

    sim = nmag.Simulation(simname)

    sim.load_mesh("cube.nmesh.h5", [("Mat", mat_Py)],
                  unit_length=edgelength)

    sim.set_m(flower_init)

    ps = SI(1e-12,"s")
    sim.relax(save = [('averages', every('time', 20*ps)),
                      ('fields', at('convergence'))])

    energy_total = sim.get_subfield_average_siv("E_total","Mat")

    return energy_total



def energy_vortexstate(length):
    global Ms
    global A
    global K1
    global easy_axis
    global lexch

    edgelength = lexch*length

    mat_Py = nmag.MagMaterial(name="Mat",
                              Ms=Ms,
                              exchange_coupling=A,
                              anisotropy=nmag.uniaxial_anisotropy(axis=easy_axis, 
                                                                  K1=K1),
                              llg_damping=1.0
                              )

    simname = "cube_vortex"+str(length)
    sim = nmag.Simulation(simname)

    sim.load_mesh("cube.nmesh.h5", [("Mat", mat_Py)],
                  unit_length=edgelength)

    sim.set_m(initial_vortex)

    ps = SI(1e-12,"s")
    sim.relax(save = [('averages', every('time', 20*ps)),
                      ('fields', at('convergence'))])

    energy_total = sim.get_subfield_average_siv("E_total","Mat")

    return energy_total


def ediff(length):
    e_vortex = energy_vortexstate(length)
    e_flower = energy_flowerstate(length)
    f=open('data.txt','a')
    f.write('%g %g %g %g\n' % (length,e_vortex,e_flower,e_vortex-e_flower))
    f.close()

    return  e_vortex - e_flower

open('data.txt','a').write('#------------\n')

# main program starts here
etrans = bisect (ediff, 8.44375, 8.425, xtol=0.01)

print "The phase transition occurs at %f" % (etrans)

