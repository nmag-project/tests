import mesh
import Numeric
pi = Numeric.pi
vertical = mesh.box(coords=[[0.0,0.0],[1.0,5.0]],outer_box=[[-5.0,-5.0],[5.0,5.0]],rod_length = 0.1)
horizontal = vertical.copy()
horizontal.rotate(0,1,pi/4., bc = True)
cross = vertical.unite(horizontal)


circle = mesh.ellipsoid(length = [1.0,1.0], shifting=[-2.0,-1.0])
compound = circle+cross

cone = mesh.conical(coords1=[0.0,0.0],rad1=2.0,coords2=[2.0,0.0],rad2=1.0,shifting = [3.0,-3.0])
hole = mesh.ellipsoid(length = [1.0,3.0], shifting=[2.0,-1.0],outer_box=[[-5.0,-5.0],[5.0,5.0]])
hole.rotate(1,0,3/4.*pi)
diff = cone-hole
compound += diff

stick = mesh.box(coords=[[0.0,0.0],[1.0,5.0]],shifting=[3.0,-2.0])
stick.rotate(1,0,pi/4.)
hole.intersect(stick)
compound += hole

compound.mesh_it(visual=True)
