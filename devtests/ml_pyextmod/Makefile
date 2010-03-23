PYTHON_VERSION=2.5
PYTHON=python$(PYTHON_VERSION)
OCAML_LIBPATH=/usr/lib/ocaml/3.10.2
NSIMROOT=../../..
OCAMLOPT=ocamlopt -I $(NSIMROOT)/snippets -I $(NSIMROOT)/pycaml -I $(NSIMROOT)/config -ccopt -fPIC 

.PHONY: all clean run

all: test

%.cmi: %.mli
	$(OCAMLOPT) -c $<

%.cmx: %.ml
	$(OCAMLOPT) -c $<

functionality.cmx: functionality.cmi

# Compile Caml source. It calls a function which is defined in snippets, but the -I ../snippets is a bit strange.

# Compile the glue which sticks together Ocaml and Python (a Python extension module calling Caml callbacks
cfunctionality.o: 
	gcc -ggdb -Wall -c functionality.c -I/usr/include/$(PYTHON) -I/usr/lib/ocaml -o cfunctionality.o
	# Note "-o cfunctionality.o" to avoid name clashes from products of
	# functionality.c and functionality.ml

bigfunctionality.so: functionality.cmx bindings.cmx
	# Link in some standard utilities
	ocamlopt -o bigfunctionality.so -output-obj unix.cmxa str.cmxa bigarray.cmxa $(NSIMROOT)/config/nsimconf.cmx $(NSIMROOT)/snippets/snippets.cmx $(NSIMROOT)/pycaml/pycaml.cmx functionality.cmx bindings.cmx

functionality.so: bigfunctionality.so cfunctionality.o
	# Stick all the necessary bits together to make a Python module
	gcc -shared --whole-archive  bigfunctionality.so $(NSIMROOT)/snippets/snippets_stubs.o $(NSIMROOT)/pycaml/pycaml_stubs.o $(NSIMROOT)/snippets/objsize.o cfunctionality.o -L$(OCAML_LIBPATH) -L/usr/lib/$(PYTHON)/config -l$(PYTHON) -lunix -lasmrun -o functionality.so -lstr -lbigarray

run: functionality.so
	# Check that it works
	$(PYTHON) -c "import functionality; print 'Test', ['FAILED', 'PASSED'][(functionality.square(1.234) == 1.234**2)]"

test: functionality.so
	py.test

clean:
	rm -f *.so *~ cfunctionality.o *.py *.cmx *.cmi *.o 

