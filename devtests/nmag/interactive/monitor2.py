#!/usr/bin/env python
"""A simple script that polls a data file for changes and then updates
the mayavi pipeline automatically.

This script is to be run like so::

 $ python poll_file.py file_to_monitor.vtk
"""

# Author: Prabhu Ramachandran <prabhu@aero.iitb.ac.in>
# Copyright (c) 2006-2007, Enthought Inc.
# License: BSD Style.

# Modified by Matteo Franchin

# Standard imports.
import os, sys
from os.path import join, abspath, dirname

# Enthought library imports
from enthought.mayavi.scripts import mayavi2
#from enthought.mayavi.sources.vtk_file_reader import VTKFileReader
from enthought.pyface.timer.api import Timer


######################################################################
# `Pollster` class.
class Pollster(object):
    """Given a file name and a mayavi2 data reader object, this class
    polls the file for any changes and automatically updates the
    mayavi pipeline.
    """
    def __init__(self, fname, data):
        """Initialize the object.

        Parameters:
        -----------
        fname -- filename to poll.
        data -- the MayaVi source object to update.
        """
        self.fname = fname
        self.data = data
        self.last_stat = os.stat(fname)

    def poll_file(self):
        # Check the file's time stamp.
        #print "Checking..."
        s = os.stat(self.fname)
        if s[-2] == self.last_stat[-2]:
            return
        else:
            self.last_stat = s
            self.update_pipeline()

    def update_pipeline(self):
        """Override this to do something else if needed.
        """
        # Force the reader to re-read the file.
        d = self.data
        d.reader.modified()
        d.update()
        # Propagate the changes in the pipeline.
        d.data_changed = True

def load_visualization(fname):
    """Given a VTK file name `fname`, this creates a mayavi2 reader
    for it and adds it to the pipeline.  It returns the reader
    created.
    """
    mayavi.load_visualization(fname)
    scene = mayavi.engine.current_scene
    vtk_reader = scene.children[0]
    return vtk_reader

timer = None

@mayavi2.standalone
def main():
    global timer

    import sys
    fname = "m.mv2" #sys.argv[1]

    vtk_reader = load_visualization(fname)
    vtk_file = vtk_reader.file_list[0]

    # Poll the file.
    p = Pollster(vtk_file, vtk_reader)
    timer = Timer(1000, p.poll_file)
    timer.Start()

    # To stop polling the file do:
    #timer.Stop()

if __name__ == '__main__':
    main()

