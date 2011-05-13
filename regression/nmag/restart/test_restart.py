import sys
import os
from os import unlink
from os.path import exists
from commands import getoutput as shexec

out1 = "out1.txt"
out2 = "out2.txt"
restart_file = "restart_1d_restart.h5"
interrupted_stage = 10
final_stage = 21

def enter_dir(*args):
    try:
        script_dir = os.path.split(__file__)[0]
    except NameError:
        return None
    initial_dir = os.getcwd()
    os.chdir(script_dir)
    return initial_dir

def exit_dir(initial_dir):
    if initial_dir != None:
        os.chdir(initial_dir)

def read_out(filename):
    f = open(filename, "r")
    content = f.read()
    f.close()

    last_stage = None
    out = []
    for line in content.splitlines():
        l = line.strip().lower()
        try:
            last_stage = int(l)
        except:
            if last_stage != None:
                out.append(last_stage)
                last_stage = None
            out.append(l)
    out.append(l)
    return out

def test_restart_1d():
    initial_dir = enter_dir()

    shexec("make clean")

    assert not (exists(out1) or exists(out2) or exists(restart_file))
    shexec("make >make.log 2>&1")

    assert exists(out1) and exists(out2)
    x = read_out(out1)
    assert len(x) == 1 and str(x[0]) == str(interrupted_stage), \
      ("First simulation (out1.txt contains the stage numbers) "
       "Should have been interrupted at stage %s, but I got %s"
       % (interrupted_stage, x[0]))

    x = read_out(out2)
    assert x == [interrupted_stage, 'stage', '<1>', str(final_stage)], \
      ("Second simulation should restart from stage %s and continue up to "
       "stage %s, but I got %s" % (interrupted_stage, final_stage, x))

    shexec("make clean") # Final cleanup
    exit_dir(initial_dir)


if __name__ == "__main__":
    test_restart_1d()

