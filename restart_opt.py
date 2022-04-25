#!/usr/bin/env python
import os

LINK='%UseSSH\n%mem=100GB\n%nprocshared=28\n'
PTCE = {1 : 'H', 2 : 'He', 3 : 'Li', 4 : 'Be', 5 : 'B', \
6  : 'C', 7  : 'N', 8  : 'O',  9 : 'F', 10 : 'Ne', \
11 : 'Na' , 12 : 'Mg' , 13 : 'Al' , 14 : 'Si' , 15 : 'P', \
16 : 'S'  , 17 : 'Cl' , 18 : 'Ar' , 19 : 'K'  , 20 : 'Ca', \
21 : 'Sc' , 22 : 'Ti' , 23 : 'V'  , 24 : 'Cr' , 25 : 'Mn', \
26 : 'Fe' , 27 : 'Co' , 28 : 'Ni' , 29 : 'Cu' , 30 : 'Zn', \
31 : 'Ga' , 32 : 'Ge' , 33 : 'As' , 34 : 'Se' , 35 : 'Br', \
36 : 'Kr' , 37 : 'Rb' , 38 : 'Sr' , 39 : 'Y'  , 40 : 'Zr', \
41 : 'Nb' , 42 : 'Mo' , 43 : 'Tc' , 44 : 'Ru' , 45 : 'Rh', \
46 : 'Pd' , 47 : 'Ag' , 48 : 'Cd' , 49 : 'In' , 50 : 'Sn', \
51 : 'Sb' , 52 : 'Te' , 53 : 'I'  , 54 : 'Xe' , 55 : 'Cs', \
56 : 'Ba' , 57 : 'La' , 58 : 'Ce' , 59 : 'Pr' , 60 : 'Nd', \
61 : 'Pm' , 62 : 'Sm' , 63 : 'Eu' , 64 : 'Gd' , 65 : 'Tb', \
66 : 'Dy' , 67 : 'Ho' , 68 : 'Er' , 69 : 'Tm' , 70 : 'Yb', \
71 : 'Lu' , 72 : 'Hf' , 73 : 'Ta' , 74 : 'W'  , 75 : 'Re', \
76 : 'Os' , 77 : 'Ir' , 78 : 'Pt' , 79 : 'Au' , 80 : 'Hg', \
81 : 'Tl' , 82 : 'Pb' , 83 : 'Bi' , 84 : 'Po' , 85 : 'At', \
86 : 'Rn' , 87 : 'Fr' , 88 : 'Ra' , 89 : 'Ac' , 90 : 'Th', \
91 : 'Pa' , 92 : 'U'  , 93 : 'Np' , 94 : 'Pu' , 95 : 'Am', \
96 : 'Cm' , 97 : 'Bk' , 98 : 'Cf' , 99 : 'Es' ,100 : 'Fm', \
101: 'Md' ,102 : 'No' ,103 : 'Lr' ,104 : 'Rf' ,105 : 'Db', \
106: 'Sg' ,107 : 'Bh' ,108 : 'Hs' ,109 : 'Mt' ,110 : 'Ds', \
111: 'Rg' ,112 : 'Uub',113 : 'Uut',114 : 'Uuq',115 : 'Uup',\
116: 'Uuh',117 : 'Uus',118 : 'Uuo'}

def restart_opt(f):
    with open(f, 'r') as fo:
        lines = fo.readlines()
    # check if there is error information in the last 10 lines
    for i in range(len(lines)-10, len(lines)):
        line = lines[i].strip()
        if line.startswith('Bend failed for angle'):
            atoms = [x for x in line.split() if x.isdigit() or x.startswith('-')]
            print('%s failed. Please modify the angle of atoms: %s\n' % (f, atoms))
            return
        elif line.startswith('Error termination'):
            print('Error termination!!!\n')
            return
    # check where is the structure with minimum energy
    min_energy = None
    eng = None
    argmin = 0
    iters = 0
    increase = 0
    for line in lines:
        line = line.strip()
        if line.startswith('Standard orientation'):
            iters += 1
            if not min_energy or eng < min_energy:
                argmin = iters
                min_energy = eng
            else:
                increase += 1
        if line.startswith('SCF Done'):
            eng = float(line.split()[4])
    if argmin >= iters-5 and increase < iters * 0.1:
        if rst_file(f): return 
        print('Warning: cannot restart from chk file.')
    else:
        print('Warning: optmization oscillated. energy increases %d times out of %d' % (increase, iters-1))
    
    extract_stdorient(f, argmin)


def extract_stdorient(f, n):
    xyz = []

    with open(f, 'r') as fo:
        lines = fo.readlines()
   
    i = 0
    while n > 0:
        if 'Standard orientation' in lines[i]:
            n -= 1
        i += 1
    i += 4
    
    while i < len(lines):
        line = lines[i].split()
        if len(line) != 6:
            break
        xyz.append('%-4s%16s%16s%16s\n' % (PTCE[int(line[1])], line[3], line[4], line[5]))
        i += 1

    if not xyz:
        raise SystemExit(':::>_<:::restarted failed. Fail to extract structure with lowest energy!')
    
    inp = None
    for line in lines:
        if 'Input' in line:
            inp = line.strip().split('=')[1]
            break
    out = inp.split('.')[0] + '_rst.'+inp.split('.')[1]
    try:
        with open(inp, 'r') as fo:
            lines = fo.readlines()
    except FileNotFoundError:
        print(':::>_<:::restarted failed. input file %s not found' % inp)
        return 
    empty = 0
    for i, line in enumerate(lines):
        if not line or not line.split():
            empty += 1
            if empty == 2:
                end = i + 2
                break
    if '%lindawork' in lines[0].lower():
        start = 1
    else:
        start = 0
    
    with open(out, 'w') as fo:
        fo.writelines(lines[start: end])
        fo.writelines(xyz)
        fo.write('\n')
    print('\'<_\' Please check and run your new gaussian input file: %s!\n' % out)


def rst_file(f):
    with open(f, 'r') as fo:
        lines = fo.readlines()
    
    i = 0
    while i < len(lines):
        if 'Input' in lines[i]:
            inp = lines[i].strip().split('=')[1]
            break
        i += 1
    while i < len(lines):
        if '%chk' in lines[i].lower():
            chkfl = lines[i].strip().split('=')[1]
            if not os.path.isfile(chkfl):
                print('Warning: not found chk file!')
                return False
            else:
                break
        i += 1
    while i < len(lines):
        if '#' in lines[i]: 
            line = lines[i].lower()
            if 'opt' not in line:
                raise SystemExit(':::>_<:::restarted failed. Cannot locate opt in the route section!')
            line = line.split()
            for i, x in enumerate(line):
                if 'opt' in x:
                    keywords = []
                    if len(x) > 3:  
                        l = r = 3
                        while r < len(x):
                            if x[r] in ['(', ')', '=', ',']:
                                keywords.append(x[l:r])
                                l = r+1
                            r += 1
                    keywords.append('Restart')
                    line[i] = 'opt=(' + ','.join(keywords) + ')'
                    opt = ' '.join(line)

                    out = inp.split('.')[0] + '_rst.' + inp.split('.')[-1]
                    with open(out, 'w') as fo:
                        fo.write(LINK)
                        fo.write('%chk='+chkfl+'\n')
                        fo.write(opt+'\n')
                    print('\'<_\' Please check and submit the input file based on chk: %s!\n' % out)
                    return True
        i += 1
    
    return False
