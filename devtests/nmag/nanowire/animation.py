#!/usr/bin/env python
#
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
from spielberg import Path, sample

def debug():
  from IPython.Shell import IPShellEmbed
  calling_frame = sys._getframe(1)
  IPShellEmbed([])(local_ns  = calling_frame.f_locals,
                   global_ns = calling_frame.f_globals)

import mayavi

v = mayavi.mayavi()

v.load_visualization('m.mv')

c = v.renwin.camera

r = 100.0
h = 1000.0


dy0 = 20.0
camera_vars = [['ll',  1.0, [   5, -dy0, 3], [   5, 50, 1]],
               ['ll',  3.0, [   5, -dy0, 1], [   5, 50, 1]],
               ['ll',  5.0, [1000, -dy0, 1], [1000, 50, 1]]]
#               ['cl',  5.0, [], []]]

positions = Path()
lookats = Path()
viewups = Path()
for m, d, p, l in camera_vars:
    if m[0] == 'l':
        positions.add_segment(to_point=p, duration=d)
        lookats.add_segment(to_point=l, duration=d)
        viewups.add_segment(to_point=[0, 0, 1], duration=d)

    elif m[0] == 'c':
        positions.add_arc()

d = 1
positions.add_arc([1000, 50, 1],
                  from_point=[1000, -dy0, 1],
                  to_point=[1050+dy0, 50, 1],
                  duration=d)
lookats.add_segment(to_point=[1000, 50, 1], duration=d)
viewups.add_segment(to_point=[0, 0, 1], duration=d)

d = 5
positions.add_arc([500, 50, 1],
                  from_point=[1050+dy0, 50, 1],
                  to_point=[500, 50, 549+dy0],
                  duration=d)
lookats.add_segment(from_point=[500, 50, 1],
                    to_point=[500, 50, 1], duration=d)
viewups.add_arc(center=[0, 0, 0],
                from_point=[0, 0, 1],
                to_point=[-1, 0, 0],
                duration=d)

d = 2
positions.add_segment(from_point=[500, 50, 549+dy0],
                      to_point=[500, 50, 300],
                      duration=d)
lookats.add_segment(to_point=[500, 50, 1], duration=d)
viewups.add_arc(center=[0, 0, 0],
                from_point=[-1, 0, 0],
                to_point=[0, 1, 0],
                duration=d)

d = 2
positions.add_pause(duration=d)
lookats.add_pause(duration=d)
viewups.add_pause(duration=d)



vars = [positions, lookats, viewups]
sampled_vars = []
def sample_fn(t):
    sampled_vars.append([v.sample(t) for v in vars])

sample(sample_fn, positions.get_max_time())

i = 0
for position, lookat, viewup in sampled_vars:
    d = math.sqrt(sum([(pi - li)**2
                       for pi, li in zip(position, lookat)]))

    clipdist = 600.0
    c.SetPosition(position[0], position[1], position[2])
    c.SetClippingRange(d-clipdist, d+clipdist)
    c.SetFocalPoint(lookat[0], lookat[1], lookat[2])
    c.SetViewUp(viewup[0], viewup[1], viewup[2])

    #debug()


    #
    # re-render scene
    #
    v.Render()
    
    #
    # uncomment the next line to save animation in file
    #
    v.renwin.save_png('anim%03d.png' % i)
    i += 1

