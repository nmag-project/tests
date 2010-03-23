all: run ncol plot

run:
	nsim bar_relax.py --clean

ncol:
	ncol bar_relax time M_Py_0 M_Py_1 M_Py_2  > bar_relax_data_M.txt

plot:
	xmgrace  -nxy bar_relax_data_M.txt -param xmgraceplot.par -hardcopy -hdevice PNG -printfile bar_relax_data_M.png
	convert -crop 789x437+3+3 bar_relax_data_M.png bar_relax_data_M.png





