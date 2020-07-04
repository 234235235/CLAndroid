import sys

def cprint(*string):
    s = [str(s) for s in string]
    print(" ".join(s))
    #sys.stdout.write(str(string)+"\n")
    sys.stdout.flush()
