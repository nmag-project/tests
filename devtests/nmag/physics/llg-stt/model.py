# nmag4       707m 353m 7:12 4222
# nsim.model  640m 294m 4:58 2411


import math
from nsim.model import *
import nmesh

mu0 = 4e-7*math.pi

# Constants and fields
def m0(r):
    x, y, z = [xi*1e9 for xi in r]
    v = [x, y + 10, z + 25.0]
    nv = sum([xi*xi for xi in v])**0.5
    return [xi/nv for xi in v]
m = SpaceField("m", [3], subfields=True, value=Value(m0, 1.0))
M_sat = Constant("M_sat", subfields=True, value=Value(0.86e6))
gamma_GG = Constant("gamma_GG", subfields=True, value=Value(2.210173e5))
alpha = Constant("alpha", subfields=True, value=Value(0.2))
norm_coeff = Constant("norm_coeff", subfields=True, value=Value(0.1e12))
zl1 = Constant("zl1", subfields=True, value=Value(1))
zl2 = Constant("zl2", subfields=True, value=Value(1))
H_ext = SpaceField("H_ext", [3], value=Value([0, 0, 1.0e5]))
dmdt = SpaceField("dmdt", [3], subfields=True)

def add_exchange(m):
    A = 13e-12 # Exchange coupling constant
    C = Constant("C", subfields=True, value=Value(-2*A/(mu0*0.86e6) * 1e18))
    H_exch = SpaceField("H_exch", [3], subfields=True)
    m.add_quantity([C, H_exch])

    # Operator for the exchange
    op_exch = Operator("exch", "C*<d/dxj H_exch(k)||d/dxj m(k)>, j:3,  k:3")
    m.add_computation(op_exch)
    return op_exch

def add_demag(m):
    H_demag = SpaceField("H_demag", [3])
    phi1b = SpaceField("phi1b", [], restrictions="phi1b[outer]")
    phi2b = SpaceField("phi2b", [], restrictions="phi2b[outer]")
    extra = [SpaceField(n, [])
             for n in ["rho", "phi", "phi1", "phi2", "rho_s"]]
    m.add_quantity([H_demag, phi1b, phi2b] + extra)

    # Operators for the demag
    op_div_m = Operator("div_m", "  M_sat*<rho||d/dxj m(j)>"
                                 "+ M_sat*<rho||D/Dxj m(j)>, j:3")
    op_neg_laplace_phi = \
      Operator("neg_laplace_phi", "<d/dxj rho || d/dxj phi>, j:3",
               mat_opts=["MAT_SYMMETRIC", "MAT_SYMMETRY_ETERNAL"])
    op_grad_phi = Operator("grad_phi", "-<H_demag(j) || d/dxj phi>, j:3")
    op_laplace_DBC = \
      Operator("laplace_DBC",
               ("-<d/dxj phi[not outer] || d/dxj phi[not outer]>;"
                "phi[outer]=phi[outer], j:3"""),
               mat_opts=["MAT_SYMMETRIC", "MAT_SYMMETRY_ETERNAL"],
               auto_dep=False)
    op_load_DBC = \
      Operator("load_DBC",
               ("<d/dxj phi[not outer] || d/dxj phi[outer]>;"
                "(L||R)=(*||phi[outer]), j:3"),
               auto_dep=False)

    # The two linear solver for the FEM/BEM
    ksp_solve_neg_laplace_phi = KSP("solve_neg_laplace_phi", op_neg_laplace_phi,
                                    ksp_type="gmres", pc_type="ilu",
                                    initial_guess_nonzero=True,
                                    rtol=1e-5, atol=1e-5, maxits=1000000,
                                    nullspace_has_constant=False,
                                    nullspace_subfields=["phi"])
    ksp_solve_laplace_DBC = KSP("solve_laplace_DBC", op_laplace_DBC,
                                ksp_type="gmres", pc_type="ilu",
                                initial_guess_nonzero=True,
                                rtol=1e-5, atol=1e-5, maxits=1000000)

    # The BEM matrix
    bem = BEM("BEM", mwe_name="phi", dof_name="phi")

    # The LAM program for the demag
    commands=[["SM*V", op_div_m, "v_m", "v_rho"],
              ["SCALE", "v_rho", -1.0],
              ["SOLVE", ksp_solve_neg_laplace_phi, "v_rho", "v_phi1"],
              ["PULL-FEM", "phi", "phi[outer]", "v_phi1", "v_phi1b"],
              ["DM*V", bem, "v_phi1b", "v_phi2b"],
              ["SM*V", op_load_DBC, "v_phi2b", "v_rho_s"],
              ["SOLVE", ksp_solve_laplace_DBC, "v_rho_s", "v_phi2"],
              ["PUSH-FEM", "phi", "phi[outer]", "v_phi2b", "v_phi2"],
              ["AXPBY", 1.0, "v_phi1", 0.0, "v_phi"],
              ["AXPBY", 1.0, "v_phi2", 1.0, "v_phi"],
              ["SM*V", op_grad_phi, "v_phi", "v_H_demag"],
              ["CFBOX", "H_demag", "v_H_demag"]]
    prog_set_H_demag = \
      LAMProgram("set_H_demag", commands,
                 inputs=["m"], outputs=["rho", "phi", "H_demag"])

    m.add_computation([op_div_m, op_neg_laplace_phi, op_grad_phi,
                       op_laplace_DBC, op_load_DBC, ksp_solve_laplace_DBC,
                       ksp_solve_neg_laplace_phi, bem, prog_set_H_demag])

def add_zhangli_stt(m):
    lam_mwes["current_density"] = mwe_current_density
    lam_mwes["dm_dcurrent"] = mwe_dm_dcurrent
    lam_vectors["grad_m"] = nlam.lam_vector(name="v_grad_m", mwe_name="grad_m")
    lam_vectors["current_density"] = \
        nlam.lam_vector(name="v_current_density", mwe_name="current_density")
    lam_vectors["dm_dcurrent"] = \
        nlam.lam_vector(name="v_dm_dcurrent", mwe_name="dm_dcurrent")
    lam_operators["op_grad_m"] = \
        nlam.lam_operator("op_grad_m", "grad_m", "m", str_grad_m)
    template_eq_grad_m_x_current = \
        "dm_dcurrent_$MAT$(i) <- grad_m_$MAT$(i, j) * current_density(j);"
    eq_grad_m_x_current = vivify_template(template_eq_grad_m_x_current,
                                          prefix="%range i:3, j:3;\n",
                                          materials=grad_m_mats)

    op_grad_m = Operator("grad_m", "<grad_m(i, j)||d/dxj m(i)>, i:3, j:3")
    m.add_computation(op_grad_m)


H_tot = SpaceField("H_tot", [3], subfields=True)


# Equation for the effective field H_tot
eq_H_tot = Equation("H_tot", """
%range i:3;
H_tot(i) <- H_ext(i) + H_exch(i) + H_demag(i);""")

# Equation of motion
llg = Equation("llg", """
%range i:3, j:3, k:3, p:3, q:3;
dmdt(i) <- (-gamma_GG/(1 + alpha*alpha))*(eps(i,j,k)*m(j)*H_tot(k) +
           alpha*eps(i,j,k)*m(j)*eps(k,p,q)*m(p)*H_tot(q)) +
           norm_coeff*(1.0 - m(j)*m(j))*m(i);""")
"""+
           zl1 * eps(i,j,k) * m(j) * eps(k,p,q) * m(p) * dm_dcurrent(q) +
           zl2 * eps(i,j,k) * m(j) * dm_dcurrent(k)"""

# Equation for the Jacobian: we omit the third term on the RHS
llg_jacobi = Equation("llg", """
%range i:3, j:3, k:3, p:3, q:3;
dmdt(i) <- (-gamma_GG/(1 + alpha*alpha))*(eps(i,j,k)*m(j)*H_tot(k) +
           alpha*eps(i,j,k)*m(j)*eps(k,p,q)*m(p)*H_tot(q));""")

# Put everything together in a physical model
mesh = nmesh.load("mesh.nmesh.h5")
region_materials = [[], ["Py"]]
p = Model("mumag", mesh, 1e-9, region_materials)

p.add_quantity([alpha, gamma_GG, norm_coeff, m, M_sat, H_ext, H_tot, dmdt])
p.add_computation([llg, eq_H_tot])

op_exch = add_exchange(p)
add_demag(p)

# Timestepper
ts = Timestepper("ts_llg", x='m', dxdt='dmdt',
                 eq_for_jacobian=llg_jacobi, derivatives=[(H_tot, op_exch)])
p.add_timestepper(ts)
p.build()

ts.initialise(rtol=1e-6, atol=1e-6, pc_rtol=1e-2, pc_atol=1e-7)

# Now we can use the model
f = open("model.dat", "w")
f.write("%g " % 0 + "%g %g %g\n" % tuple(m.compute_average().as_float()))
for i in range(1, 101):
  t = i*10e-12
  ts.advance_time(t)
  f.write("%g " % t + "%g %g %g\n" % tuple(m.compute_average().as_float()))
  vm = m.compute_average().as_float()
  print sum([mi*mi for mi in vm])**0.5

print "Number of steps", ts.get_num_steps()
f.close()
