import nmag
from nmag import SI, every, at

ocaml.init_hlib("/rhome/ak8w07/mumag/nmag/lib/libhmatrix-1.3.so")


#create simulation object
hp = {}
hp['nfdeg'] = 3
hp['nmin'] = 20
hp['p'] = 4
hp['eta'] = 2.0
hp['eps'] = 0.000001

sim = nmag.Simulation(name="bar_relax",use_hlib=True, use_pvode=False, hlib_params=hp)

mat_Py = nmag.MagMaterial( name="Py",
                           Ms=SI(0.86e6, "A/m"),
                           exchange_coupling=SI(13.0e-12, "J/m"),
                           llg_damping=0.5)


sim.load_mesh("bar30_30_100.nmesh.h5", [("Py", mat_Py)],
              unit_length=SI(1e-9, "m"))

sim.set_m([1, 0, 1])

ps = SI(1e-12,"s")
sim.relax(save = [('averages', every('time', 5*ps)),
                  ('fields', at('convergence'))])
