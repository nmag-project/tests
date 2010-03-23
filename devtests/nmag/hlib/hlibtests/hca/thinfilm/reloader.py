import os
import simulation

def renew():
    os.chdir('../')
    reload(simulation)
    os.chdir('thinfilm70_70_5')
