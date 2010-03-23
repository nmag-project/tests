"""This program shows the different protections that PyTables offer to
the user in order to insure a correct data injection in tables.

Example to be used in the second tutorial in the User's Guide.

"""

from numarray import *
from tables import *

N=10000

# Another way to describe the columns of a table
Event = {
    "name"        : StringCol(length=16),
    "time"        : Float64Col(shape=1),
    "M"    : Float64Col(shape=(N,3)),
    }

# Open a file in "w"rite mode
fileh = openFile("tutorial2.h5", mode = "w")
# Get the HDF5 root group
root = fileh.root
# Create the groups:
for groupname in ["Events","Mesh"]:
    group = fileh.createGroup(root, groupname)
# Now, create and fill the tables in Particles group



for tablename in ("TEvent1",):
    # Create a table in Events group
    table = fileh.createTable(root.Events, tablename, Event,
                           "Events: "+tablename)
    # Get the record object associated with the table:
    event = table.row
    # Fill the table with 257 events
    for i in xrange(1,25):
	print "working on i=%d" % i
        event['name']  = 'Event: %6d' % (i)
        event['time']  = float(i)
	event['M']=array(i*arange(N*3),shape=(N,3))
        event.append()
    # Flush the buffers
    print "About to call flush"

    table.flush()
    print "Done flush."

# Finally, close the file (this also will flush all the remaining buffers!)
fileh.close()


print "closed file"
f=openFile('tutorial2.h5')
for node in f:
    print node
f.close()


#This is good. Not sure how to read the data back best, but saving is
#efficient. 16/01/2007 20:41
