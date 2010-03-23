
catch_switches = True
if catch_switches:
    #scan for important pytest switches, which we remove from sys.argv
    #(so that nmag does not get confused by them) and pass to py.test
    #directly. HF 30/10/08

    #Addition: this catching of py.test switches seems to be required only
    #sometimes. In fact, I have only seen the problem so far when trying
    #to run pytest_nsim directly in
    #nsim/tests/regression/nmag/demag_twomat.


    accepted_pytest_args = ['-s','--nocapture','-v','--verbose','-x','--exitfirst','-l','--showlocals','--nomagic','--collectonly','--tkinter']
    accepted_pytest_args_with_argument = ['-k','--testonlythisfile','-T']

    import sys,copy
    args = copy.copy(sys.argv)
    print "args are",args
    pytest_args = []
    for i in range(len(args)):
        if args[i] in accepted_pytest_args:
            pytest_args.append(args[i])
            sys.argv.remove(args[i])
        elif args[i] in accepted_pytest_args_with_argument:
            if args[i] == '--testonlythisfile' or args[i]=='-T':
                pass #this is our own addition to the py.test argument language
            else:
                pytest_args.append(args[i])
            sys.argv.remove(args[i])

            #nasty hack: pyfem3 and python behave differently when
            #dealing with sys.argv:
            #  fangohr@eta:~/tmp$ ../svn/nsim/bin/nsim test.py "one two"
            #  ['test.py', 'one', 'two']
            #  fangohr@eta:~/tmp$ python test.py "one two"
            #  ['test.py', 'one two']
            #  fangohr@eta:~/tmp$ cat test.py
            #  import sys
            #  print sys.argv

            #We can thus not pass the argument "-test_slow -test_mpi" correctly
            #We cheat by using '@' as a place holder for space. (Not nice).
            if "@" in args[i+1]: #dealing with "-test_slow -test_mpi"
                print "Found argument with spaces:",args[i+1]
                pytest_args.append(''+args[i+1].replace('@'," ")+'')
            else:
                pytest_args.append(args[i+1])
            sys.argv.remove(args[i+1])
            


    print "pytest_main.py: Caught switches '%s' for py.test" % pytest_args
else:
    pytest_args=None




import py
py.test.cmdline.main(args=pytest_args)

