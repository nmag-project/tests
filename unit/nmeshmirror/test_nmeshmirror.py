import nmag
import os

#work out in which directory the data files are
org_dir = os.getcwd()


def test_nmeshmirror():
    os.chdir(os.path.split(__file__)[0])

    #define my non-periodic mesh

    points = [[0,0],[1,0],[0,1],[1,1]]

    simplices = [[0,2,3],[0,1,3]]

    regions=[1,1]

    import nmesh

    mesh = nmesh.mesh_from_points_and_simplices(points,simplices,regions,[],0,False)

    mesh.save('org.nmesh')

    import nmesh.visual
    nmesh.visual.plot2d_ps(mesh,'org.ps')

    # mirror along the x axis (horizontal direction)
    command = "../../../bin/nmeshmirror org.nmesh 1e-6 1e-6 1,0 mirror1.nmesh"

    status = os.system(command)

    assert status==0, "after command '%s' status is %s" % (command,status)

    periodicmesh = nmesh.load('mirror1.nmesh')

    nmesh.visual.plot2d_ps(periodicmesh,'mirror1.ps')

    for i in range(4):
        assert mesh.points[i] == periodicmesh.points[i], \
            "org/mirror1, point %i differs: %s %s" % \
            (i,mesh.points[i],periodicmesh.points[i])

    assert [2.0, 0.0] in periodicmesh.points," [2.0, 0.0] not in periodic points"
    assert [2.0, 1.0] in periodicmesh.points," [2.0, 1.0] not in periodic points"

    command = "../../../bin/nmeshmirror org.nmesh 1e-6 1e-6 -1,0 mirror2.nmesh"

    status = os.system(command)

    assert status==0, "after command '%s' status is %s" % (command,status)

    periodicmesh = nmesh.load('mirror2.nmesh')

    nmesh.visual.plot2d_ps(periodicmesh,'mirror2.ps')

    for i in range(4):
        assert mesh.points[i] == periodicmesh.points[i], \
            "org/mirror2, point %i differs: %s %s" % \
            (i,mesh.points[i],periodicmesh.points[i])

    assert [-1.0, 0.0] in periodicmesh.points," [-1.0, 0.0] not in periodic points"
    assert [-1.0, 1.0] in periodicmesh.points," [-1.0, 1.0] not in periodic points"

    # mirror along the y axis (vertical direction)
    command = "../../../bin/nmeshmirror org.nmesh 1e-6 1e-6 0,1 mirror3.nmesh"

    status = os.system(command)

    assert status==0, "after command '%s' status is %s" % (command,status)

    periodicmesh = nmesh.load('mirror3.nmesh')

    nmesh.visual.plot2d_ps(periodicmesh,'mirror3.ps')

    for i in range(4):
        assert mesh.points[i] == periodicmesh.points[i], \
            "org/mirror3, point %i differs: %s %s" % \
            (i,mesh.points[i],periodicmesh.points[i])

    assert [0.0, 2.0] in periodicmesh.points," [0.0, 2.0] not in periodic points"
    assert [1.0, 2.0] in periodicmesh.points," [1.0, 2.0] not in periodic points"


    # mirror along the x and y axis (horizontal and vertical directions)
    command = "../../../bin/nmeshmirror org.nmesh 1e-6 1e-6 1,1 mirror4.nmesh"

    status = os.system(command)

    assert status==0, "after command '%s' status is %s" % (command,status)

    periodicmesh = nmesh.load('mirror4.nmesh')

    nmesh.visual.plot2d_ps(periodicmesh,'mirror4.ps')

    for i in range(4):
        assert mesh.points[i] == periodicmesh.points[i], \
            "org/mirror4, point %i differs: %s %s" % \
            (i,mesh.points[i],periodicmesh.points[i])

    assert [2.0, 0.0] in periodicmesh.points," [2.0, 0.0] not in periodic points"
    assert [2.0, 1.0] in periodicmesh.points," [2.0, 1.0] not in periodic points"
    assert [0.0, 2.0] in periodicmesh.points," [0.0, 2.0] not in periodic points"
    assert [1.0, 2.0] in periodicmesh.points," [1.0, 2.0] not in periodic points"



    os.chdir(org_dir)
