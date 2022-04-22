#!/usr/bin/env python
import sys, os

KEY = "Predicted change"

def checkcommand():
    n = len(sys.argv)
    if n == 2:
        if os.path.exists(sys.argv[1]):
            return sys.argv[1]
        raise SystemExit("Error: %s not exist." % sys.argv[1])
    raise SystemExit("Usage: python compress_optlog.py opt.log")

def compress(fl):
    out  = fl.split(".")[0] + "_c.log"
    fout = open(out, "w")
    fin = open(fl, "r")
    nstep = 0
    buffer = []
    for line in fin.readlines():
        if nstep == 0:
            fout.write(line)
        else:
            buffer.append(line)
        if KEY in line:
            nstep += 1
            prebuffer = list(buffer)
            buffer = []
    fout.write("".join(prebuffer))
    fout.write("".join(buffer))
    fin.close()
    fout.close()
    print("Finish: check %s, original step number: %s" % (out, nstep))

def main():
    f =  checkcommand()
    compress(f)

if __name__ == "__main__":
    main()
