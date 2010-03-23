import nsim
from nsim.si_units.si import mu0
from nmag import SI

exchange_coupling = SI(13.0e-12, "J/m")
m_sat = SI(0.86e6, "A/m")
exchange_length = (2.0*exchange_coupling/(mu0*m_sat**2))**0.5

def bar_size(d):
    return (5.0*d, d, 0.1*d)

if __name__ == "__main__":
    oommf_src = "mumag2.mif.orig"
    oommf_dest = "mumag2.mif"
    print "producing the OOMMF mif file " \
      "'%s' from '%s'" % (oommf_src, oommf_dest)

    L, d, t = bar_size(5.0*exchange_length.value)
    cx = cy = cz = t
    subst = [
      ("M_SAT", m_sat.value),
      ("EXCHANGE_COUPLING", exchange_coupling.value),
      ("BAR_L", L),
      ("BAR_d", d),
      ("BAR_t", t),
      ("CELL_x", cx),
      ("CELL_y", cy),
      ("CELL_z", cz) ]

    subst_str = " ".join(["-e 's/%s/%s/g'" % (k, str(r)) for (k, r) in subst])
    import commands
    cmnd = "sed %s %s > %s" % (oommf_src, subst_str, oommf_dest)
    print cmnd
    print commands.getoutput(cmnd)
