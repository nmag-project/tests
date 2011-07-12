def sim():
  import nmag
  from nmag import SI
  import nsim.setup

  from nsim.testtools import get_test_mesh
  mesh_filename = get_test_mesh(size="small")

  s = nmag.Simulation(phi_BEM=nmag.default_hmatrix_setup)
  material = nmag.MagMaterial("Py")
  s.load_mesh(mesh_filename, [("region", material)], unit_length=SI(1e-9, "m"))
  s.set_m([1, 0, 0])
  s.advance_time(0*SI("s"))

def test_two_hmatrices_in_same_file():
  import ocaml
  sim()
  ocaml.sys_check_heap()
  sim()
  ocaml.sys_check_heap()

if __name__ == "__main__":
  test_two_hmatrices_in_same_file()

