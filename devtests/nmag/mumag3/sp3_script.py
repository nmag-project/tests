from nmag.common import *
from nsim.si_units.si import mu0

import math, random
from scipy.optimize import bisect

# Setting of material parameters
Ms = SI(1.0e6, "A/m")
A  = SI(13.0e-12, "J/m")

# Magnetostatic energy density
Km = (mu0*Ms**2)/2.0

# Computing uniaxial anisotropy for standard problem 3 
K1 = 0.1*Km
easy_axis = [0, 0, 1]

# Defining exchange length
#lexch = SI(math.sqrt(A.value/Km.value), "m")
lexch = (A/Km)**0.5

# Initial configuration for flower state computation
flower_m0 = [0, 0, 1]

def vortex_m0(r):
    """Creating a vortex-like initial magnetisation with the core pointing in x
    direction. The analytic expression for the vortex has been taken from

    Guslienko et al. "Field evolution of magnetic vortex state in ferromagnetic 
    disks", APPLIED PHYSICS LETTERS, Volume 78, Number 24

    The size of the vortex core is assumed to be twice as large as the diameter
    of the vortex core.

    """

    global lexch

    x, y, z = [xi*1e9 for xi in r]

    #b = 2*lexch.value
    b = 2*float(lexch/SI('m'))
    rho = x**2 + y**2

    phi = math.atan2(z, x)
    m_phi = math.sin(2*math.atan(rho/b))

    mx = math.sqrt(1.0 - m_phi**2)
    my =  m_phi*math.cos(phi)
    mz = -m_phi*math.sin(phi)
    
    magnitude = math.sqrt(mx*mx + my*my + mz*mz)
    result = [mx/magnitude, my/magnitude, mz/magnitude]
    return result

def energy_flowerstate(name, length, m0):
    global Ms, A, K1, easy_axis, lexch, flower_init

    edgelength = lexch*length

    mat_Py = MagMaterial(name="Mat",
                         Ms=Ms,
                         exchange_coupling=A,
                         anisotropy=uniaxial_anisotropy(axis=easy_axis,
                                                        K1=K1),
                         llg_damping=1.0)

    simname = "%s%020.15f" % (name, length)
    sim = Simulation(simname)

    sim.load_mesh("cube.nmesh.h5", [("Mat", mat_Py)],
                  unit_length=edgelength)

    sim.set_m(m0)

    ps = SI(1e-12,"s")
    sim.relax(save = [('averages', every('time', 20*ps)),
                      ('fields', at('convergence'))])

    energy_total = sim.get_subfield_average_siv("E_total", "Mat")
    return energy_total

def ediff(length):
    e_vortex = energy_flowerstate("cube_vortex", length, vortex_m0)
    e_flower = energy_flowerstate("cube_flower", length, flower_m0)
    e_diff = e_vortex - e_flower

    f = open('data.txt', 'a')
    f.write('%g %g %g %g\n' % (length, e_vortex, e_flower, e_diff))
    f.close()

    return  e_diff

open('data.txt','a').write('#------------\n')

# Main program starts here
e_trans = bisect(ediff, 8.44375, 8.425, xtol=0.01)

print "The phase transition occurs at %f" % e_trans

