NMAG_ROOT=../../../../src

cube.nmesh.h5: cube.neutral
	nmeshimport --netgen cube.neutral cube.nmesh.h5

cube.neutral: cube.geo
	netgen -geofile=cube.geo -meshfiletype="Neutral Format" -meshfile=cube.neutral -batchmode

examesh.nmesh.h5:
	(HERE=`pwd` && cd $(NMAG_ROOT)/utils/cubicmesh && make \
	 && ./examesh $$HERE/examesh.nmesh,1.0:20,1.0:23,1.0:20)
	nmeshpp -c examesh.nmesh examesh.nmesh.h5

