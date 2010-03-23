import nsim
from nsim.si_units.si import mu0
from nmag import SI
import math, commands

degrees = math.pi/180.0

# This file contains the common specification of the problem to be solved
# with nmag, magpar, OOMMF. This file writes the input files for magpar
# OOMMF as well as the file for plotting with gnuplot.
# It takes the file.orig and creates a corrsesponding file, replacing
# the parameters, such as the saturation magnetisation, etc.

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
# The problem specification data follows

# Available meshes: the meshes have all the same aspect ratio: 5 x 1 x 0.1,
# they are scaled by a factor d. This dictionary gives them as a function
# of d.
meshes = {5.0:"meshes/film2_d005.h5"}
meshes = {5.0:"meshes/film_d005.h5"}

sim_name = "bar"
exchange_coupling = SI(13.0e-12, "J/m")
m_sat = SI(0.86e6, "A/m")
exchange_length = (2.0*exchange_coupling/(mu0*m_sat**2))**0.5

mesh_unit_length = SI(1e-9, "m")
d_in_exchange_lengths = 5.0
d = float(d_in_exchange_lengths*exchange_length/SI("m"))

bar_size_x = 5.0*d
bar_size_y = d
bar_size_z = 0.1*d
bar_mesh = meshes[d_in_exchange_lengths]


# In polar coordinates the direction of (1, 1, 1) is given by
# phi = 45 and theta = 54.73... degrees (not phi = theta = 45
# as one may intuitively think!)
Hext_theta = 54.735610317245346*degrees
Hext_phi = 45*degrees

choice = "hysteresis loop" # Just to do different test for comparison
choic = "one stage"
if choice == "hysteresis loop":
    Hext_initial = 0.6*m_sat
    Hext_final = -0.2*m_sat
    num_stages = 200
    save_averages_every_step = None
    save_averages_every_stage = 1
elif choice == "one stage":
    Hext_initial = 0.6*m_sat
    Hext_final = 0.4*m_sat
    num_stages = 1
    save_averages_every_step = 10
    save_averages_every_stage = 1

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
# This part of the file creates the simulation files for OOMMF and Magpar

cp, sp = math.cos(Hext_phi), math.sin(Hext_phi)
ct, st = math.cos(Hext_theta), math.sin(Hext_theta)
vHext_direction = [st*cp, st*sp, ct]
vHext_initial = [h*Hext_initial for h in vHext_direction]
vHext_final = [h*Hext_final for h in vHext_direction]
Hext_step = (Hext_final - Hext_initial)/num_stages

def sed(src_file, dest_file, subst, comment=False):
    subst_str = " ".join(["-e 's/%s/%s/g'" % (k, str(r)) for (k, r) in subst])
    cmnd = "sed %s %s > %s" % (src_file, subst_str, dest_file)
    if comment: print "producing '%s' from '%s'" % (dest_file, src_file)
    print cmnd
    print commands.getoutput(cmnd)

if __name__ == "__main__":
    L, d, t = bar_size_x, bar_size_y, bar_size_z
    cx = cy = cz = 0.5*t
    # Magpar wants fields in KA/m
    hextini = float(Hext_initial/SI(1e3, "A/m"))
    hfinal = float(Hext_final/SI(1e3, "A/m"))
    hstep = float(Hext_step/SI(1e3, "A/m"))
    ec = float(exchange_coupling/SI("J/m"))
    oommf_save_stage = ""
    oommf_save_step = ""
    if save_averages_every_stage:
        oommf_save_stage = "Schedule DataTable archive " \
                          "Stage %d" % save_averages_every_stage
    if save_averages_every_step:
        oommf_save_step = "Schedule DataTable archive " \
                          "Step %d" % save_averages_every_step
    subst = [
      ("SIM_NAME", sim_name),
      ("MESH_UNIT_LENGTH_IN_M", float(mesh_unit_length/SI("m"))),
      ("M_SAT_T", (m_sat*mu0).value),
      ("M_SAT", m_sat.value),
      ("EXCHANGE_COUPLING", ec),
      ("BAR_L", L),
      ("BAR_d", d),
      ("BAR_t", t),
      ("CELL_x", cx), # OOMMF stuff follows
      ("CELL_y", cy),
      ("CELL_z", cz),
      ("HEXTINI", hextini), # Magpar stuff follows
      ("HFINAL", hfinal),
      ("HSTEP", hstep),
      ("HTHETA", Hext_theta),
      ("HPHI", Hext_phi),
      ("HIX", float(vHext_initial[0]/SI("A/m"))),
      ("HIY", float(vHext_initial[1]/SI("A/m"))),
      ("HIZ", float(vHext_initial[2]/SI("A/m"))),
      ("HFX", float(vHext_final[0]/SI("A/m"))),
      ("HFY", float(vHext_final[1]/SI("A/m"))),
      ("HFZ", float(vHext_final[2]/SI("A/m"))),
      ("NUM_STAGES", num_stages),
      ("OOMMF_SAVE_STAGE", oommf_save_stage),
      ("OOMMF_SAVE_STEP", oommf_save_step),
       ]

    sed("oommf/bar.mif.orig", "oommf/bar.mif", subst, comment=True)
    sed("magpar/allopt.txt.orig", "magpar/allopt.txt", subst, comment=True)
    sed("magpar/bar.krn.orig", "magpar/bar.krn", subst, comment=True)
    sed("results/plot.gnp.orig", "results/plot.gnp", subst, comment=True)

    # Now select the mesh for magpar
    print commands.getoutput('nmeshpp -m %s magpar/%s.inp' % (bar_mesh, sim_name))
