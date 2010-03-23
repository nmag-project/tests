import nmag
import sys

def test_import_ocaml():
    import ocaml
    assert type(ocaml) == type(sys)

def test_import_nmag_known_to_fail():
    # There seems to be an IPython-related failure, which I don't have
    # the time to debug now. (jacek 2007-10-10)
    import nmag
    assert type(nmag) == type(sys)



