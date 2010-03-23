"""Example showing how the class type can be changed on the fly"""

class A:
    def __init__(self,name):
        self.name=" I am an A:"+name
        self.__class__ = B
        B.__init__(self,'new name A->B')

    def only_A(self):
        print "Can only call this for A"


class B:
    def __init__(self,name):
        self.name=" I am a B:"+name
    def only_B(self):
        print "Can only call this for B"




a=A('A')
print a.name
print dir(a)
a.only_B()
b=B('B')
print a,a.name
print b,b.name
