all: run ncol plot

run:
	nsim thinfilm_relax.py --clean

ncol:
	ncol thinfilm_relax time M_Py_0 M_Py_1 M_Py_2  > thinfilm_relax_data_M.txt

plot:
	xmgrace  -nxy thinfilm_relax_data_M.txt -param xmgraceplot.par -hardcopy -hdevice PNG -printfile thinfilm_relax_data_M.png
	convert -crop 789x437+3+3 thinfilm_relax_data_M.png thinfilm_relax_data_M.png





