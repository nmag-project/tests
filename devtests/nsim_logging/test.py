import nmag
import ocaml

ocaml.nlog_setupLogger('test')

def mypythonhandler(level,msg):
    print "mypythonhandler: %d '%s'" % (level,msg)

#nmag.setup.pyfeatures.to_ocaml_features()

#print "YYYYYYYYY About to call ergister handler"

#print "YYYYYYYYY get_feature:",ocaml.snippets_get_feature('nmag','slavelog')
ocaml.nlog_register_handler('test',mypythonhandler)
#print "ZZZ get_feature:",ocaml.snippets_get_feature('nmag','slavelog')

#print message on all nodes

ocaml.nlog_log_mpi('test',51,'High priority Test message from all nodes')
print "Setting loglevel to 20"
ocaml.nlog_setLogLevel('test',20)
ocaml.nlog_log_mpi('test',10,'Debug Test message from all nodes (should not be shown)')
print "Setting loglevel to 10"
ocaml.nlog_setLogLevel('test',10)
ocaml.nlog_log_mpi('test',10,'Debug Test2 message from all nodes')

nmag.ipython()
