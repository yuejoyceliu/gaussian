#!/usr/bin/env python

import os, sys

def checkcommand():
    if len(sys.argv)!=6:
        message = "Usage: python freqlog2den.py gaussian-freq-log Egrain1 Imax1 Isize Emax2\n" \
                + "  Egrain1: energy grain in units of cm-1. suggest=5\n" \
                + "  Imax1: number of array elements in first segment of double array. suggest=1000\n" \
                + "  Isize: total size of double array. suggest=3000\n" \
                + "  Emax2: maximum energy (cm-1) for calculation. suggest=80000"
        raise SystemExit(message)
    else:
        return sys.argv[1:6]

def readfreqlog(flog):
    if not os.path.exists(flog):
        raise SystemExit("Error: %s Not Exits!" % flog)
    with open(flog, "r") as fo:
        lines = fo.readlines()
    freq = []
    for line in lines:
        line = line.lstrip()
        if line.startswith("Frequencies"):
            freq.extend(line.split()[2:])
    return freq

def create_densum_input(params):
    [flog, egrain1, imax1, isize, emax2] = params
    freq = readfreqlog(flog)
    if float(freq[-1]) > float(egrain1) * (float(imax1) - 1):
        raise SystemExit("Error: Egrain1*(Imax1-1) (%sx(%s-1)) not greater than %s!" % (egrain1, imax1, freq[-1]))
    with open("densum.dat", "w") as fo:
        fo.write(flog[:180] + "\n")
        fo.write(flog[:10] + "\n")
        fo.write(",".join([str(len(freq)), "0", "'HAR'", "'CM-1'"]) + "\n")
        fo.write(",".join(params[1:]) + "\n")
        for i, v in enumerate(freq):
            fo.write(",".join([str(i+1), "vib", v, "0", "1"]) + "\n")
        fo.write("\n")
    print("**\(^o^)/** Found %d frequencies! Next run: /sw/contrib/multiwell-2022/bin/densum" % len(freq))

if __name__=="__main__":
    params = checkcommand()
    create_densum_input(params)
