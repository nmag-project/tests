import os

from nsim.setup import get_exec_path

netgen_bin = "netgen"
nmeshpp_bin = "nmeshpp"
nmeshimport_bin = "nmeshimport"

def netgen_mesh_from_file(geo_filename, mesh_filename, mesh_type=None,
                          keep_neu=False, keep_logs=False):
    if mesh_type == None:
        mesh_type = os.path.splitext(mesh_filename)[1][1:]
        print mesh_type
        if mesh_type not in ["neu", "nmesh", "h5", "nmesh.h5"]:
            raise ValueError("Cannot determine mesh type from extension. "
                             "Please specify the mesh type explicitly using "
                             "the optional argument \"mesh_type\".")

    if mesh_type == "neu":
        tmp_filename = mesh_filename

    else:
        tmp_filename = os.path.splitext(mesh_filename)[0] + ".neu"

    os.system('%s -geofile=%s -moderate -meshfiletype="Neutral Format" '
              '-meshfile=%s -batchmode' % (netgen_bin, geo_filename,
                                           tmp_filename))

    if not keep_logs:
        for log_filename in ["ng.ini", "test.out"]:
            try:
                os.remove(log_filename)
            except:
                pass

    if mesh_type == "neu":
        return

    exts = ["nmesh", "h5", "nmesh.h5"]
    if mesh_type in exts:
        if not mesh_filename.endswith("." + mesh_type):
            raise ValueError("The file name must have the extension '.%s' "
                             "for files of type '%s'."
                             % (mesh_type, mesh_type))
        os.system("%s --netgen %s %s" % (nmeshimport_bin, tmp_filename,
                                         mesh_filename))
        if not keep_neu:
            os.remove(tmp_filename)

def netgen_mesh_from_string(s, mesh_filename, mesh_type=None,
                            geo_filename=None,
                            keep_geo=False, keep_neu=False):
    if geo_filename == None:
        geo_filename = os.path.splitext(mesh_filename)[0] + ".geo"

    f = open(geo_filename, "w")
    f.write(s)
    f.close()

    netgen_mesh_from_file(geo_filename, mesh_filename,
                          mesh_type=mesh_type,
                          keep_neu=keep_neu)
    if not keep_geo:
        os.remove(geo_filename)

geo_file = """
algebraic3d
solid bar = orthobrick (0, 0, 0; 100, 30, 30) -maxh=%.1f;
tlo bar;
"""

maxh_list = [4.0, 3.0, 2.5, 2.2, 2.1, 2.0]
#maxh_list = [2.1]
mesh_filename_list = ["bar-maxh%s.nmesh.h5" % maxh for maxh in maxh_list]

def get_meshinfo(meshinfo_filename="mesh.info"):
    """Get mesh information and cache it to file, so that next time
    the function is called the info can be retrieved quickly without
    being re-generated."""

    # We need to know how many nodes each mesh has
    # This info is stored in a file which we read.
    # If the file is not there, we generate it!
    if not os.path.exists(meshinfo_filename):
        from mesh_gen import mesh_filename_list
        import commands
        col_num_points = []
        for mesh_filename in mesh_filename_list:
            out = commands.getoutput("%s -i %s" % (nmeshpp_exec, mesh_filename))
            lines = out.splitlines()
            for line in out.splitlines():
                if line.endswith("points"):
                    num_points = line.split()[0]
            col_num_points.append(num_points)

        f = open(meshinfo_filename, "w")
        for entry in col_num_points:
            f.write("%s\n" % entry)
        f.close()

    # Read mesh info from the file
    f = open(meshinfo_filename, "r")
    lines_left = f.read().splitlines()
    f.close()
    return lines_left

if __name__ == "__main__":
    for i, maxh in enumerate(maxh_list):
        netgen_mesh_from_string(geo_file % maxh, mesh_filename_list[i])

