MESHFILE=bar60_60_100


all: netgen meshconvert meshorder run1

netgen:
	netgen -geofile=$(MESHFILE).geo -meshfiletype="Neutral Format" -meshfile=$(MESHFILE).neutral -batchmode


meshconvert:
	nmeshimport --netgen $(MESHFILE).neutral $(MESHFILE).nmesh.h5

meshorder:
	nmeshpp --reordernodes $(MESHFILE).nmesh.h5 $(MESHFILE)_ordered.nmesh.h5 


#mirror:
#	nmeshmirror $(MESHFILE).nmesh 1e-6 1e-6 0,0,1 $(MESHFILE)_double.nmesh 1
#	nmeshpp -c $(MESHFILE)_double.nmesh $(MESHFILE)_double.nmesh

showpartitions:
	nmeshpp --partitioning=2  $(MESHFILE)_ordered.nmesh.h5 partition.vtk
	mayavi -d partition.vtk -m SurfaceMap


run1:
	mpirun -np 2 ../../../../bin/nsim parallel.py --clean


ncol1:
	../../../../bin/ncol parallel time M_Py_0 M_Py_1 M_Py_2  > data_M.txt

plot1:
	xmgrace  -nxy data_M.txt -param xmgraceplot.par -hardcopy -hdevice PNG -printfile data_M.png

	xmgrace  -nxy data_M.txt -nxy oommf_M -param xmgraceplot.par -hardcopy -hdevice PNG -printfile data_M_OOMMF.png

