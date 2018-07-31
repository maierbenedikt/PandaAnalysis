#!/usr/bin/env python

# imports and load libraries
from array import array
from glob import glob
from re import sub
from sys import argv,exit
import sys
from os import environ,system,path,remove
from argparse import ArgumentParser
import subprocess

sname = argv[0]
parser = ArgumentParser()
parser.add_argument('--silent', action='store_true')
parser.add_argument('--cfg', type=str, default='common')
parser.add_argument('--skip_missing', action='store_true')
parser.add_argument('arguments', type=str, nargs='+')
args = parser.parse_args()
arguments = args.arguments
VERBOSE = not args.silent
skip_missing = args.skip_missing
argv=[]

import ROOT as root
from PandaCore.Tools.Misc import *
from PandaCore.Utils.load import Load

if 'leptonic' in args.cfg:
    from PandaCore.Tools.process_leptonic import *
    xsecscale = 1000
else:
    from PandaCore.Tools.process import *
    xsecscale = 1

sys.path.append(environ['CMSSW_BASE'] + '/src/PandaAnalysis/T3/merging/configs/')
cfg = __import__(args.cfg)

Load('Normalizer')

# global variables
pds = {}
for k,v in processes.iteritems():
    if v[1]=='MC':
        pds[v[0]] = (k,v[2])  
    else:
        pds[v[0]] = (k,-1)

submit_name = environ['SUBMIT_NAME']
user = environ['SUBMIT_USER']

inbase = environ['SUBMIT_OUTDIR']
outbase = environ['PANDA_FLATDIR']

hadd_cmd = 'hadd -k -f '

if VERBOSE:
    suffix = ''
else:
    suffix = ' > /dev/null '

# helper functions
def hadd(inpath,outpath):
    if type(inpath)==type('str'):
        infiles = glob(inpath)
        if len(infiles) > 1: # if 1 file, use mv
            logger.info(sname,'hadding %s into %s'%(inpath,outpath))
            cmd = '%s %s %s %s'%(hadd_cmd, outpath,inpath,suffix)
            system(cmd)
            return True
    else:
        infiles = inpath
    if len(infiles)==0:
        logger.warning(sname,'nothing hadded into '+outpath)
        return False
    elif len(infiles)==1:
        logger.info(sname,'moving %s to %s'%(inpath[0],outpath))
        if infiles[0].startswith('/tmp'):
            mv = 'mv'
        else:
            mv = 'cp'
        cmd = '%s -v %s %s'%(mv,infiles[0],outpath)
    else:
        cmd = '%s %s '%(hadd_cmd, outpath)
        for f in infiles:
            if path.isfile(f):
                cmd += '%s '%f
        logger.info(sname,'hadding into %s'%(outpath))
    if VERBOSE: logger.info(sname,cmd)
    system(cmd+suffix)
    return True

def normalizeFast(fpath,opt):
    xsec=-1
    if type(opt)==float or type(opt)==int:
        xsec = opt
    else:
        try:
            xsec = processes[fpath][2]
        except KeyError:
            for k,v in processes.iteritems():
                if fpath in k:
                    xsec = v[2]
    if xsec<0:
        logger.warning(sname,'could not find xsec, skipping %s!'%opt)
        return
    xsec *= xsecscale
    logger.info(sname,'normalizing %s (%s) ...'%(fpath,opt))
    n = root.Normalizer();
    if not VERBOSE:
        n.reportFreq = 2
    n.NormalizeTree(fpath,xsec)

def merge(shortnames,mergedname):
    to_skip = []
    for shortname in shortnames:
        xsec = None
        if 'monotop' in shortname:
            pd = shortname
            xsec = 1
        elif 'Vector' in shortname:
            tmp_ = shortname
            replacements = {
                'Vector_MonoTop_NLO_Mphi-':'',
                '_gSM-0p25_gDM-1p0_13TeV-madgraph':'',
                '_Mchi-':'_',
                }
            for k,v in replacements.iteritems():
                tmp_ = tmp_.replace(k,v)
            m_V,m_DM = [int(x) for x in tmp_.split('_')]
            params = read_nr_model(m_V,m_DM)
            if params:
                xsec = params.sigma
            else:
                xsec = 1
        elif 'Scalar' in shortname:
            tmp_ = shortname
            replacements = {
                'Scalar_MonoTop_LO_Mphi-':'',
                '_13TeV-madgraph':'',
                '_Mchi-':'_',
                }
            for k,v in replacements.iteritems():
                tmp_ = tmp_.replace(k,v)
            m_V,m_DM = [int(x) for x in tmp_.split('_')]
            params = read_r_model(m_V,m_DM)
            if params:
                xsec = params.sigma
            else:
                xsec = 1
        elif shortname in pds:
            pd = pds[shortname][0]
            xsec = pds[shortname][1]
        else:
            for shortname_ in [shortname.split('_')[0],shortname.split('_')[-1]]:
                if shortname_ in pds:
                    pd = pds[shortname_][0]
                    xsec = pds[shortname_][1]
                    break
        inpath = inbase+shortname+'_*.root'
        success = hadd(inpath, split_dir + '%s.root'%(shortname))
        if success:
            normalizeFast(split_dir + '%s.root'%(shortname),xsec)
        if not success:
            if not skip_missing:
                logger.error(sname, 'Could not merge %s, exiting!'%shortname)
                exit(1)
            else:
                to_skip.append(shortname)
    to_hadd = [split_dir + '%s.root'%(x) for x in shortnames if x not in to_skip]
    hadd(to_hadd, merged_dir + '%s.root'%(mergedname))
    for f in to_hadd:
        if f.startswith('/tmp'):
            system('rm -f %s'%f)


args = {}

for pd in arguments:
    if pd in cfg.d:
        args[pd] = cfg.d[pd]
    else:
        args[pd] = [pd]

for pd in args:
    unmerged_files = glob("{0}/{1}_*.root".format(environ['SUBMIT_OUTDIR'],pd))
    unmerged_size = 0
    for unmerged_file in unmerged_files:
        unmerged_size += path.getsize(unmerged_file)
    if unmerged_size > 16106127360: # 15 GB
        disk="scratch5"
    else:
        disk="tmp"
    split_dir = '/%s/%s/split/%s/'%(disk, user, submit_name)
    merged_dir = '/%s/%s/merged/%s/'%(disk, user, submit_name)
    for d in [split_dir, merged_dir]:
        system('mkdir -p ' + d)
    merge(args[pd],pd)
    merged_file = merged_dir + '%s.root'%(pd)
    hadd(merged_file ,outbase) # really an mv
    if merged_file.startswith('/tmp'):
        system('rm -f %s'%merged_file)
    logger.info(sname,'finished with '+pd)

