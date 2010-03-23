import types
import tables

import logging
log=logging

c_dofnamelength = 128
c_fieldnamelength = c_dofnamelength
c_unitstringlength = 128
c_stringvalue = 128  #for example localtime string
c_dof_maxind = 64

timesteps_in_h5_file = []

def create_file(filename,mode='w'):
    f=tables.openFile(filename,mode)
    f.close()

def tagfile(f,filetype,version):
    """Add 'tag' in /etc/filetype and /etc/fileversion.

    We use this to identify the different types of h5 files we have.

    So far these are

    nmesh (only the mesh: points, simplices, simplex regions are compulsory)

    nsimdata (several time dependend fields)

    """

    version = str(version)
    filetype= str(filetype)

    if type(f) == types.StringType: #filename being given:
        fh = tables.openFile(f,'a')
    else:
        fh = f
    
    if not hasattr(fh.root,'etc'):
        etcgroup = fh.createGroup("/", 'etc', 'Configuration and version data')

    if not hasattr(fh.root.etc,'filetype'):
        fh.createArray("/etc", 'filetype', [filetype],title='data file type')
        log.debug("Have tagged file %s with filetype '%s'" % (fh.filename,filetype))
    else:
        checktag_filetype(f,filetype)
            
    if not hasattr(fh.root.etc,'fileversion'):
        fh.createArray("/etc", 'fileversion', [version],title='data file type version')
        log.debug("Have tagged file %s with version %s" % (fh.filename,version))
    else: 
        checktag_version(f,version)


def checktag_version(f,version):
    version = str(version)
    version_okay = False
    fileversion = f.root.etc.fileversion[0]
    log.debug("checktag_version, filename=%s, file version=%s, required version=%s" % (f.filename,fileversion,version))
    if fileversion == version:
        version_okay = True
    else:
        raise NfemUserError,"File is of version %s but you try to use with code for version %s" % (f.root.etc.fileversion[0],version)
    return version_okay
def checktag_filetype(f,filetype):
    filetype = str(filetype)
    filetype_okay = False
    filefiletype=f.root.etc.filetype[0]
    log.debug("checktag_filetype, filename=%s, filetype=%s, required filetype=%s" % (f.filename,filefiletype,filetype))
    if  filefiletype == filetype:
        filetype_okay = True
    else:
        raise NfemUserError,"File %s is of type '%s' but you try to use it as '%s'" % (f.filename,f.root.etc.filetype[0],filetype)

    return filetype_okay
    

def checktag(f,filetype,version):
    return checktag_version(f,version) and checktag_filetype(f,filetype)


def tables_floatCol(floattype):

    if floattype == '64':
        return tables.Float64Col
    elif floattype == '32':
        return tables.Float32Col
    else:
        raise UserError,"only know float types '32' and '64' but got '%s' from you" % floattype

def tables_floatAtom(floattype):

    if floattype == '64':
        return tables.Float64Atom
    elif floattype == '32':
        return tables.Float32Atom
    else:
        raise UserError,"only know float types '32' and '64' but got '%s' from you" % floattype


def append_averages(filename,names,values,units,floattype='32'):

    f=tables.openFile(filename,'r+')
    checktag(f,'nsimdata','0.1')

    if hasattr(f.root.etc,'metadataaverages'):
        #Check that fields provided are already known.
        known_names = f.root.etc.metadataaverages.cols.name[:]

        for name in names:
            if not name in known_names:
                log.error( "Known names are %s" % str(known_names))
                log.error( "Known names for averaged data are %s" % known_names)
                raise NfemUserError, "This file (%s) has been created without '%s'. It cannot be added now." % (filename,name)

    else: #create metadataaverages table

        #Create table with metadataaverages, keeping the names of the doftypes,
        #fields, the units and maxind data
        metadataaveragestablestruct = {}
        metadataaveragestablestruct['name'] = tables.StringCol(c_fieldnamelength)
        metadataaveragestablestruct['unit'] = tables.StringCol(c_unitstringlength)

        #create table
        myfilter = tables.Filters(complib='zlib',complevel=5)
        table = f.createTable(f.root.etc,'metadataaverages',metadataaveragestablestruct,\
                              title='Metadataaverages on fields and dofs', filters=myfilter)
        table.flush()


        #Now populate this, one row per name
        row=table.row
        
        for name,unit in map(None,names,units):
            row['name']=name
            row['unit']=repr(unit)

            if type(unit) == types.StringType: #i.e. not SI object but, eg, 'deg'
                pass
            elif unit.value != 1.0:
                log.warn("You are using '%s' as the unit for average %s values" % (name,str(unit)))
                log.warn("We'll let you, but you deviate from the convention")
                log.warn("to save all data in SI units.")
                raise ValueError,"Tried to save data with non-SI unit. Stopping for now"
            row.append()
        table.flush()
    #now we have added the metadata


    #check whether the right subgroups exit already
    if not hasattr(f.root,'data'):
        datanode = f.createGroup('/','data','Simulation data')
        log.debug("Adding /data")

    if not hasattr(f.root.data,'averages'):
        #fieldsnode = f.createGroup('/data','averages','nsim fields spactially averaged')
        log.debug("Adding /data/averages")

        tablestruct = {}

        #create table
        for name,unit,value in map(None,names,units,values):
            #create table if necessary

            log.debug("Creating /data/averages-table. Have "+\
                      "received name=%s and type=%s (value=%s)"\
                      % (name,str(type(value)),str(value)))

            if type(value) == types.FloatType:
                tablestruct[name]= tables_floatCol('64')(shape=1)
            elif type(value) == types.IntType:
                tablestruct[name]= tables.Int64Col()
            elif type(value) == types.StringType:
                tablestruct[name]=tables.StringCol(c_stringvalue)
            elif type(value) == types.ListType:
                nd_value = numpy.array(value)
                tablestruct[name]=tables_floatCol('64')(shape=nd_value.shape)
            else:
                msg = "name = %s has value %s which is of type %s" % \
                      (name,str(value),str(type(value)))
                msg +="\n Don't know how to handle this type"
                raise ValueError,msg

        myfilter = tables.Filters(complib='zlib',complevel=5)

        #from IPython.Shell import IPShellEmbed
        #ipshell = IPShellEmbed([])
        #ipshell()
    

        
        table = f.createTable(f.root.data,'averages',tablestruct,\
                              title='Spatial averages of fields', filters=myfilter)

        table.flush()

    #Now populate this, one row per dof

    table = f.getNode(f.root.data,'averages')
    
    row=table.row

    step = None

    for name,value,unit in map(None,names,values,units):
        log.debug("About to add %s with value %s to /data/averages in %s" %\
                  (name,str(value),f.filename))
        row[name]=value

	#find step
	if name=='step':
	    step = value

    row.append()
    table.flush()

    timesteps_in_h5_file.append(step)

    f.flush()
    f.close()


filename='test.h5'
create_file(filename)

tagfile(filename,'nsimdata','0.1')


names=['time','x','y','z','step']
values = [0.1,1.,2.,3.,0]
units = ['s','m','m','m','']
append_averages(filename,names,values,units,floattype='32')
