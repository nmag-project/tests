cube.nmesh.h5: cube.neutral
	nmeshimport --netgen cube.neutral cube.nmesh.h5

cube.neutral: cube.geo
	netgen -geofile=cube.geo -meshfiletype="Neutral Format" -meshfile=cube.neutral -batchmode
