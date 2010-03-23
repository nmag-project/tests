import nmag

def test_refcount():
    import sys
    import ocaml


    a=["data"]*100

    count1 = sys.getrefcount(a)

    print "refcount(a),",count1
    print "About to call ocaml function"
    ocaml.debug_absorb_list(a)

    count2 = sys.getrefcount(a)
    print "refcount(a),",count2
    ocaml.sys_check_heap()
    count3 = sys.getrefcount(a)
    print "refcount(a),",count3

    assert count1 == count3, "Refcounter problem"



if __name__ == "__main__":
    test_refcount()





