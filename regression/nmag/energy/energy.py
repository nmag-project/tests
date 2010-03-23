import nmag
from nsim.si_units import SI
import math

m = nmag.MagMaterial("Py",
                     Ms=SI(0.86e6, "A/m"))

s = nmag.Simulation()

s.load_mesh("cube.nmesh.h5",
            [("cube", m)],
            unit_length=SI(1e-9, "m"))

theta0 = 0.0
theta1 = math.pi
theta_n = 10

phi0 = 0.0
phi1 = 2*math.pi
phi_n = 10

def out(s):
  f = open("shapeanis.dat", "a")
  f.write(s)
  f.close()

for ti in range(theta_n - 1):
  theta = theta0 + (theta1 - theta0)*ti/theta_n
  for pi in range(phi_n - 1):
    phi = phi0 + (phi1 - phi0)*pi/phi_n
    m = [math.sin(theta)*math.cos(phi),
         math.sin(theta)*math.sin(phi),
	 math.cos(theta)]
    s.set_m(m)
    s.save_data(fields='all')
    a = s.get_subfield_average_siv("E_total", "Py")
    out("%s %s %s\n" % (theta, phi, a))
  out("\n")

