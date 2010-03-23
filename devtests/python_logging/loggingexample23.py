import logging, sys, logging.handlers

def setup_logger(loggername='root',
		 stdoutlevel=logging.WARNING,
		 logfilelevel=logging.DEBUG,
		 logdir='log',logfilename='root.log'):

    """This functions sets up a logger with name LOGGERNAME. 
    It will print both to stdout and to a file, with given 
    priorities.
    """

    #write log file into subdirectory
    import os.path
    if not os.path.exists(logdir):
	os.mkdir('log')

    #this is the logger for general log entries
    #such as 'starting mesh calculation' or
    #'starting simulation' and general stuff like that.
    #We will call it loggername.
    logger = logging.getLogger(loggername) 

    #if you need to refer to this anywhere in the code, just say
    #"logger = logging.getLogger(loggername)" then you can use it as in
    #logger.warning('my warning message')
    
    #we choose a format for the handlers of this logger 
    #see here http://www.python.org/doc/2.3.5/lib/node296.html
    formatter = logging.Formatter('%(name)s :%(asctime)s %(module)s %(filename)s %(lineno)s %(levelname)s  %(message)s')

    #finally we would like to attach this logging object to a file 
    logfile_handler = logging.handlers.RotatingFileHandler(os.path.join(logdir,logfilename),
							   maxBytes=1024*1024,backupCount=5)
    #and format this nicely
    logfile_handler.setFormatter(formatter)

    #Set the level of messages that are recorded
    #(standard levers are: CRITICAL, ERROR, WARNING, INFO, DEBUG)
    logfile_handler.setLevel(logfilelevel)

    #and add this handler to the logger
    logger.addHandler(logfile_handler)

    #We'd like to have less logging data on the screen (here sys.stdout)
    #create another handler, producing less output on screen (sys.stdout)
    stdout_handler = logging.StreamHandler(sys.stdout)

    #use same format as above
    stdout_handler.setFormatter(formatter)

    #but different level
    stdout_handler.setLevel(stdoutlevel)

    #add to logger
    logger.addHandler(stdout_handler) 

    #set logger level to DEBUG to pass all log messages to handlers
    logger.setLevel(logging.DEBUG)

    #log our first message
    logger.info('Have just set up logger "%s"' % loggername)

    return logger

def localfunction():
    """This demonstrates how to get to the logger with out passing the root logger
    instance around"""

    logger = logging.getLogger('root')
    logger.warning('Am in local function.')
    logger.info('Am in local function.')
    logger.debug('Am in local function.')
    logger.critical('Am in local function.')


#Need to call this once in the main program
rootlogger = setup_logger(loggername='root')

#testing:
rootlogger.info('----------------------------Main program starts -----------')
rootlogger.info('CVS: $Header$ ')
rootlogger.error('We have a problem')
rootlogger.info('While this is just chatty')
rootlogger.warning('This is a warning?')
rootlogger.debug('This is a low lever debug message.')

localfunction()

#maybe we'd like a second logger for mesh?
meshlogger = setup_logger(loggername='mesh')
meshlogger.info('Have a mesh logger now')
meshlogger.critical('Critical to have a mesh logger now')


#There are more sophisticated tools such as sending log messages via SMTP or 
#automatic rotation of logfiles. See here, for example
#http://www.python.org/doc/2.3.5/lib/node288.html
#and here for an overview:
#http://www.python.org/doc/2.3.5/lib/module-logging.html


#Here is a useful introduction to logging:
#http://www.onlamp.com/pub/a/python/2005/06/02/logging.html


rootlogger.info('----------------------------Main program ends -----------')

logger=logging.getLogger('root')
logger.critical("Final comment")

