def main():


    def driver_do(nr_piece, n,mesh):

        print "Iteration: %d" %(n)

    rod_length=0.1
    my_mdefaults=ocaml.mesher_defaults
    my_gendriver=ocaml.make_mg_gendriver(100,driver_do)

    # create a mesh
    square = ocaml.body_box([0.0,0.0,0.0],[1.0,1.0,1.0])
    density="""
    {
    density=1.0;
    }
    """

    mesh = ocaml.mesh_bodies_raw(my_gendriver,my_mdefaults, [-10.0,-10.0,-10.0], [10.1,10.1,10.1], 1,[square], rod_length,density)

if __name__ == "__main__":
    main()

