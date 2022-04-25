#!/usr/bin/env python
"""
 Usage 1: python optlog2gjf.py file-name-opt.log
 Descriptions: Extract the optimized structure from the log file if it is optimized, otherwise generate restart input file.
 Usage 2: python optlog2gjf.py
 Descriptions: Extract the optimized structures or generate restart input files for all opt log files in the current directory.
"""
import sys,os,glob
from restart_opt import restart_opt

LINK='%UseSSH\n%mem=100GB\n%nprocshared=28\n'
#ROUTE = '# opt=modredundant um062x/6-31+g(d,p) pop=npa scf=(xqc,tight)'
#ROUTE = '# opt m062x/6-31+g(d,p) pop=none scf=(xqc,tight) scrf=(pcm,solvent=water,read) geom=allcheck'
ROUTE ='# opt m062x/6-31+g(d,p) pop=none scf=(xqc,tight)'
#ROUTE = '# freq ub3lyp/6-31+g(d,p) pop=none scf=(xqc,tight)'
#ROUTE = '# opt freq=hinderedrotor b3lyp/6-31+g(d,p) pop=none scf=(xqc,tight)'
#ROUTE = '# td(NStates=70) um062x/6-31+g(d,p) pop=npa scf=(xqc,tight)'
def main():
    files = check_command()
    print('Default: %s' % ROUTE)
    out = []
    for f in files:
        if optlog2gjf(f): out.append(f)
    if out: print('**\(^O^)/**found %d optimized structures' % len(out))
    for f in out:
        print(' ' + f.split('.')[0])

def check_command():
    if len(sys.argv) == 2:
        f = sys.argv[1]
        if f.split('.')[-1].lower() != 'log':
            print('Warning: the input file should be optimization log file.')
        if not os.path.isfile(f):
            raise SystemExit('Error: %s not found!' % f)
        return [f]
    else:
        return glob.glob('*.log')

def optlog2gjf(f):
    with open(f, 'r') as fo:
        lines = fo.readlines()

    # check if it is opt job
    i, length = 0, len(lines)
    while i  < length:
        if lines[i].lstrip().startswith('#'):
            if 'opt' not in lines[i].lower():
                print('Warning: %s is not a opt log.' % f)
                return
            break
        i += 1

    # check if the job finish
    while i < length:
        if 'Stationary point found' in lines[i]:
            break
        i += 1    
    if i == length:
        print('Warning: %s opt not finish!' % f)
        restart_opt(f)
        return False
    else:
        get_optstruct(f, i)
        return True

def get_optstruct(f, i):
    with open(f, 'r') as fo:
        lines = fo.readlines()

    while i < len(lines):
        if '#' in lines[i]:
            break
        i += 1
    
    data = ''.join([l.strip() for l in lines[i-1:]])
    result = data.split('\\\\')
    i = 0
    while i < len(result) and not result[i].startswith('#'):
        i += 1
    i += 2

    result = result[i].split('\\')

    name = f.split('.')[0]
    out = open(name+'_opt.gjf', 'w')
    out.write(LINK)
    out.write('%chk=' + name + '.chk' + '\n')

    route = ROUTE
    temp = result[0].split(',')
    if len(temp) == 2 and temp[0].isdigit() and temp[1].isdigit():
        chgmul = ' '.join(temp) + '\n'
        if temp[1] != '1':
            route = route.split()
            for i, x in enumerate(route):
                if len(x) >=5 and x[:5] in ['b3lyp', 'm062x', 'wb97x']:
                    route[i] = 'u' + x
            route = ' '.join(route)

    else:
        print('Warning: not found charge and multiplicity, use -1, -1 by default')
        chgmul = '-1 -1\n'

    out.write(route + '\n\n')
    out.write('Complex ' + name +'\n\n')
    out.write(chgmul)

    for line in result[1:]:
        line = line.split(',')
        out.write('%-4s%16s%16s%16s\n' % (line[0], line[1], line[2], line[3]))
    out.write('\n')
    out.close()

if __name__ == '__main__':
    main()
    



