from ctypes import cdll, c_int, c_double, POINTER

_foo = cdll.LoadLibrary('./libfoo.so')
_foo.bar.restype = c_int
_foo.bar.argtypes = [POINTER(c_double), c_int]

def bar(data):
    return _foo.bar(data, len(data))

data = (c_double*10)(0,2,4,6,8,10,12,14,16,18)
#lenplusone = bar(data)
#print "lenplusone is ",lenplusone

_foo.test.restype = POINTER(c_double)
_foo.test.argtypes = [POINTER(c_double), c_int]

def test(data):
    return _foo.test(data, len(data))

result = test(data)
print "result ",result

for i in range(10):
    print data[i],result[i]

print """So the data is passed to C by reference, and we get
pointers to data back. However, be warned that if we exceed
this array (i.e. data[10]), then Python has no way of telling
this and we may cause a segfault."""


