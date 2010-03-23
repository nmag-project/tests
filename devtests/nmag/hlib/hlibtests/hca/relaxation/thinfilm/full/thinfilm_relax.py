import nmag
from nmag import SI, every, at


sim = nmag.Simulation(name="thinfilm_relax")

mat_Py = nmag.MagMaterial( name="Py",
                           Ms=SI(0.86e6, "A/m"),
                           exchange_coupling=SI(13.0e-12, "J/m"),
                           llg_damping=0.5)


sim.load_mesh("thinfilm230_230_5.nmesh.h5", [("Py", mat_Py)],
              unit_length=SI(1e-9, "m"))

sim.set_m([0, 0, 1])

ps = SI(1e-12,"s")
sim.relax(save = [('averages', every('time', 5*ps)),
                  ('fields', at('convergence'))])
