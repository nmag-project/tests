MESHFILE=bar60_60_200


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


results:
	../../../../bin/ncol parallel time M_Py_0 M_Py_1 M_Py_2  > data_M.txt

plot1:
	xmgrace  -nxy data_M.txt -param xmgraceplot.par -hardcopy -hdevice PNG -printfile data_M.png
	convert -crop 789x437+3+3 data_M.png data_M.png

	xmgrace  -nxy data_M.txt -nxy oommf_M -param xmgraceplot.par -hardcopy -hdevice PNG -printfile data_M_OOMMF.png
	convert -crop 789x437+3+3 data_M_OOMMF.png data_M_OOMMF.png	

ncol2:
	ncol bar_relax time M_Py_0 M_Py_1 M_Py_2  > bar_relax_data_M.txt

plot2:
	xmgrace  -nxy bar_relax_data_M.txt -param xmgraceplot2.par -hardcopy -hdevice PNG -printfile bar_relax_data_M.png
	convert -crop 789x437+3+3 bar_relax_data_M.png bar_relax_data_M.png

ncol3:
	ncol bar_relax2 time M_Py_0 M_Py_1 M_Py_2  > bar_relax2_data_M.txt

plot3:
	xmgrace  -nxy bar_relax2_data_M.txt -param xmgraceplot2.par -hardcopy -hdevice PNG -printfile bar_relax2_data_M.png
	convert -crop 789x437+3+3 bar_relax2_data_M.png bar_relax2_data_M.png

vtk:
	../../../../bin/nmagpp --range 0 --vtk bar_initial.vtk bar
	../../../../bin/nmagpp --range 6 --vtk bar_final.vtk bar	

clean:
	rm bar_30_30_100_dat* 


_rst:
	echo "Only for testing: -> example2.html"
	rst2html example2.txt example2.html
