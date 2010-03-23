#!/bin/bash

#This script creates several directories containing thinfilm meshes, which are
#created by the program ./cubicmesh written by Matteo.

#first some paths are defined
working_dir=`pwd`
cubicmesh_dir='/home/aknittel/mumag/nsim/utils/cubicmesh'
cubicmesh='$(cubicmesh_dir)/cubicmesh'

#Here I define a parameter list, further meshes can be added by just extending
#the list

param="50:20,50:20,5:2"
#param="90:36,90:36,5:2 110:44,110:44,5:2 130:52,130:52,5:2 150:60,150:60,5:2 170:68,170:68,5:2 190:76,190:76,5:2"

#check whether Matteo's meshing script has been compiled
cd ${cubicmesh_dir}
if [ ! -f cubicmesh ]
    then
    make cubicmesh
fi
cd ${working_dir}

#in this loop the mesh files are created
for mesh in ${param}
do
  xmesh=`echo ${mesh} | cut -d ',' -f1`
  ymesh=`echo ${mesh} | cut -d ',' -f2`
  zmesh=`echo ${mesh} | cut -d ',' -f3`
  xdim=`echo ${xmesh} | cut -d ':' -f1`
  ydim=`echo ${ymesh} | cut -d ':' -f1`
  zdim=`echo ${zmesh} | cut -d ':' -f1`
  
  name=thinfilm${xdim}_${ydim}_${zdim}

  if [ -f ${name}/${name} ]
      then
      echo -e "The mesh ${name} has already been created.\n"
  else
      if [ ! -d ${name} ]
	  then
	  mkdir ${name}
      fi
      cd ${cubicmesh_dir}
      ./cubicmesh ${name},${mesh}
      mv ${name} ${working_dir}/${name}
      cd ${working_dir}/${name}
      nmeshpp -c ${name} ${name}".nmesh.h5"
      touch dimensions.txt
      echo $xdim >> dimensions.txt
      echo $ydim >> dimensions.txt
      echo $zdim >> dimensions.txt
      rm ${name}
      cd ../
  fi
done

exit 0