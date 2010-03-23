import tables
from tables.nodes import FileNode 
import os

def save_mesh(filename):
    pass

def insert_file(h5fh,where,name,title,filename):
    fnode=FileNode.newNode(h5fh,where=where,name=name,title=title)
    fnode.write(open(filename,'r').read())

    import time
    fnode.attrs.creationdate=time.asctime()
    fnode.attrs.path=os.path.abspath(filename)
    import socket
    fnode.attrs.host=socket.getfqdn()
    
    fnode.close()        

def save_simulation(filename):
    f=tables.openFile(filename,'r+')
    f.createGroup(f.root,'sim',title='Simulation code and configuration files')
    sourcefilename='hdf5.py'
    insert_file(f,where="/sim",name="source",\
                title="The source code of the main program '%s'" % sourcefilename,\
                filename=sourcefilename)
    f.createGroup(f.root,'log',title='Log files')
    f.close()

def createfile(name,flag):
    myfilter = tables.Filters(complevel=5, complib="zlib")
    f=tables.openFile(name,flag,filters=myfilter)
    f.close()

def appendfield(filename,field):
    pass

def savefield(filename,field):
    if os.path.exists(filename):
        appendfield(filename,field)
    else:
        createfile(filename,'w')
        save_mesh(filename)
        save_simulation(filename)


def get_sorted_data():
    myfields = nmag2._get_nfem_fields()
    mdata = numpy.array(myfields.m.m_Py.data)
    msites = numpy.array(myfields.m.m_Py.site)
    #get order right, double check for 2nd order
    sort_ind = msites.argsort(axis=0)
    mdatasorted = numpy.take(mdata,sort_ind)
    



os.remove('test.h5')

savefield('test.h5','test.h5')


f=tables.openFile('test.h5')
node = f.root.sim.source
fnode = FileNode.openNode(node)
for line in fnode.readlines():
    print repr(line)
fnode.close()

f=open('test.h5','r')
#print str(f)
f.close()

os.system('h5ls -r test.h5')
#os.system('ptdump -av test.h5')
#os.system('ptdump -d test.h5:/sim/source')
