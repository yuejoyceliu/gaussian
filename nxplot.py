#!/usr/bin/env python

'''
 AUTHOR: Yue Liu
 EMAIL: yueliu96@uw.edu
 Created: 12/16/2018
Usage: python nxplot.py
run this script 'python nxplot.py' in INITIAL_CONDITIONS directory
First, it will check if I* finished. If all finished,it will first merge all I* files together to give you I_merged file. All important data are in final_optput.1.* file, which contains transition information from state 1 to state *
Second, it goes to I_merged directory, to generate cross-section.dat by $NX/nxinp to calculate absorption spectra
'''
import os,glob,shutil,sys,subprocess
import time

def checkfinish(fd):
    fl = fd+'/initcond.log'
    completed = False
    n_cond = 0
    if not os.path.exists(fl):
        print(' Warning: %s Not Exists!' % fl)
    else:
        with open(fl,'r') as fo:
           ctts = fo.readlines()
        for line in ctts:
            if 'Done' in line:
                n_cond += 1
            elif 'NEWTON-X ends here' in line:
                completed = True
        if not completed: print(' Warning: %s Not Finished!' % fd)
    return completed, n_cond

def nx_merge(n):
    with open('temptno','w') as fo:
        fo.write(str(n))
    sdo1 = 'module load contrib/newtonX; $NX/merge_initcond.pl < temptno'
    print('Number of directories to be merged: %d\n\n\tPlease wait a little bit...' % n)
    p = subprocess.Popen(sdo1,stdout=subprocess.PIPE,shell=True)
    a = p.wait()
    os.remove('temptno')
    if a!=0:
        raise SystemExit(':::>_<:::Fail to merge jobs to I_merged!')

def nx_spec():
    nstates = len(glob.glob('I_merged/final_output.1.*'))+1
    with open('I_merged/temptinp','w') as fo:
        fo.write('5\n1\n1\n2-'+str(nstates)+'\nF\n0\n-1\nlocal\n1\nlorentz\n0.1\n310\n1\n0.005\n3\n7\n')
    sdo2 = 'cd I_merged; module load contrib/newtonX; $NX/nxinp < temptinp'
    p = subprocess.Popen(sdo2, shell=True)
    a = p.wait()
    os.remove('I_merged/temptinp')
    if a!=0:
        raise SystemExit(':::>_<:::Fail to process spectra data!')

def nxplot():
    try:
        if os.path.exists('I_merged'):
            raise SystemExit('I_merged Exists! Remove and try it again!')
        allI = glob.glob('I*')
        n = len(allI)
        if n==0:
            raise SystemExit(':::>_<::: I* subfolder Not Found!')
        print('\'<_\' %d jobs found! Start to check if they finish...' % n)
        notfinished = []
        n_cond = 0
        allI.sort(key=lambda x: (len(x),x))
        for I in allI:
            status,t_n = checkfinish(I)
            if status==False: notfinished.append(I)
            n_cond += t_n
        print('\'<_\' Finish checking! %s initial conditions found!' % n_cond)
        nx_merge(n)
        nx_spec()
        with open('I_merged/cross-section.dat') as fo:
            lines = fo.readlines()
        x = float(lines[-1].split()[1])
        _, npoints = checkfinish('I_merged')
        if len(notfinished)>0:
            print('Reminder: the following tasks not completed:')
            print('\t'.join(notfinished))
        print('Reminder: Found %d initial conditions completed!' % n_cond)
        print('**\(^O^)/** %d geometries are merged to I_merged/cross-section.dat!' % npoints) 
    except:
        err=sys.exc_info()
        print('python error in line: %s' % err[2].tb_lineno )
        raise SystemExit(err[1])

if __name__=='__main__':
    nxplot()
