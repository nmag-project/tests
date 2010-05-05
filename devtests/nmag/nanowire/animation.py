#!/usr/bin/env python
#
# this is how to animate a mayavi-file (here heart.mv) 
# (No interaction allowed)
#
# Be sure to be in the examples subdirectory so heart.mv (mayavi's
# summary of the scene to visualise), heart.vtk (the data) and
# custom16.lut (the colour lookup table) are available.  
#
# This is pretty much the example from
# http://mayavi.sourceforge.net/docs/guide/c827.html.

import sys, math

def debug():
  from IPython.Shell import IPShellEmbed
  calling_frame = sys._getframe(1)
  IPShellEmbed([])(local_ns  = calling_frame.f_locals,
                   global_ns = calling_frame.f_globals)

import mayavi

v = mayavi.mayavi()

v.load_visualization('vtk/m.mv')

c = v.renwin.camera
c.SetFocalPoint(500, 50, 5)

r = 100.0

status = {'img_number': 0}

def save_png():
    if 1:
        v.renwin.save_png('anim%04d.png' % status['img_number'])
    status['img_number'] += 1


import glob

# directory listing...

input_list = glob.glob('vtk/m-*.vtk')
input_list.sort()
input_list = [input_list[i]
              for i in range(0, len(input_list), 5)] # decimation

# grab the DataVizManager list
dvms = v.get_dvm_names()

# Bring the camera close to the center of the wire
dz = 50
#for i in range(270):
if 1:
    i = 269
    j = max(0, i - 100)
    z = 2000 - j*10
    c.SetPosition(500, 50, z)
    c.SetClippingRange(z-dz, z+dz)

    v.Render()
    save_png()

for i in range(50):
    v.Render()
    save_png()

countdown = 100
i0 = 0
for n, datafile in enumerate(input_list):
    for j in dvms:
        # grab a handle to the DVM
        dvm = v.mayavi.data_viz_mgr[j]

        # follow the pipeline, and load in the new data file
        ds  = dvm.get_data_source()
        rdr = ds.get_reader()

	previous = rdr.GetFileName()
	if not ("mesh" in previous):
          rdr.SetFileName(datafile)
          ds.Update()
          ds.update_references()

    # re-render the scene
    v.Render()
    save_png()

