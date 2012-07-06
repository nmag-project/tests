From: 	curtis s.j. (sjc3g08) <sjc3g08@soton.ac.uk>
	Subject: 	RE: Granual media meshing
	Date: 	6 July 2012 11:55:51 GMT+01:00
	To: 	Fangohr H. <H.FANGOHR@soton.ac.uk>

Hi Hans, 

I've looked into the script I wrote and have attached this. Most of the instructions are included in the documentation in the --help option. The script produces a .geo file which can then be read by gmsh and a .py script which can be used with nmag. The .py script only loads the mesh and has the material definitions with the anisotropy defined as upwards, disturbed at a random small angle which is controlled by the standard deviation provided in the script. 

Not sure how familiar you are with gmsh so I'll give a quick run down of producing the mesh file. When using the .geo file with gmsh, the first step is to set the element size, this is in Options --> Mesh --> General, under "Min/Max element size" which is similar to the --maxh in netgen. The mesh can then be created through Mesh (in the dropdown) --> 3D. Save the mesh with File --> save as then choose to save the file as a *.msh, and then choose version 1 in the next popup. This is what I've found has worked best for me in the past. As long as the mesh is imported (with --gmsh option) as the same filename as the others with the .nmesh.h5 extension, it should work with the .py script once the rest of the simulation script has been built up.

As always, let me know if there's anything else, It might be best to use my other email address (stucurtis15@hotmail.com), certainly in a couple of months time.

Stuart
