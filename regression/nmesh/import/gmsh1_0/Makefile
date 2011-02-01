include ../../../../config/tools.inc

sphere.nmesh: sphere.msh
	$(NMESHIMPORT) --gmsh sphere.msh sphere.nmesh

sphere2.nmesh:  sphere.msh
	cp -f sphere.msh sphere2.msh
	gzip -f sphere2.msh
	$(NMESHIMPORT) --gmsh sphere2.msh.gz sphere2.nmesh

sphere.msh: sphere.geo
	gmsh -3 -format msh1 -optimize_netgen -order 1 -o sphere.msh sphere.geo 

clean:
	rm -f sphere.msh sphere.nmesh 

