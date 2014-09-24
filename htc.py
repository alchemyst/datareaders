#!/usr/bin/env python

# Author: Carl Sandrock

import sys
import numpy
import pandas
import re
import io
import os
from StringIO import StringIO
import logging

logging.basicConfig(level=logging.INFO)

__version__ = 0.2


blockheader = re.compile("([A-Za-z][A-Za-z ]*):")

knownblocks = ['Curve Name', 
               'Curve Values', 
               'Results', 
               'Sample', 
               'Evaluation', 
               'Method',
               'Sample Holder',
               'Pan', ]

def curveparser(blockname, block):
    colnames = ["Index", "Ts", "Tr", "Value"]
    table = pandas.read_table(StringIO('\n'.join(block)),
                              header=None,
                              names=colnames,
                              delimiter=' +',
                              skiprows=[0,1],
                              index_col='Index')
    return {blockname: block}

def flatten(blockname, block):
    return {blockname: '|'.join(block)}

def sampleholderparser(blockname, block):
    return {'Pan Description': block[0],
            'Pan Mass': float(block[1].split(':')[1].strip()),
            'Pan Material': block[2].split(':')[1].strip()}

def sampleparser(blockname, block):
    description, mass = block[0].split(',')
    return {'Sample Description': description,
            'Sample Mass': float(mass.split()[0])}

def remove(blockname, block):
    return {}
    
blockparsers = {'Curve Values': curveparser,
                'Pan': sampleholderparser,
                'Sample Holder': sampleholderparser,
                'Method': flatten,
                'Sample': sampleparser,
                'Curve Name': flatten,
                'Results': remove,
                }

def read_htc_file(f):
    if hasattr(f, 'next'):
        infile = f
    else:
        infile = io.open(f, encoding='utf-8')

    state = 'Waiting'
    
    curves = []
    curvenumber = 0
    blocknumber = None

    for line in infile:
        # State switching logic
        if not line.strip():
            state = "Waiting"
            continue
        m = blockheader.match(line)
        if m:
            state = "Read block"
            blockdata = []
            blockname = m.groups()[0]
            oldblocknumber = blocknumber
            blocknumber = knownblocks.index(blockname)
            # We assume that blocks going in the wrong order means a
            # new block.
            if oldblocknumber is None or blocknumber < oldblocknumber:
                curve = {'Filename': os.path.basename(f),
                         'Number': curvenumber}
                curvenumber += 1
                curves.append(curve)
                logging.debug(" -- new curve -- ")
            curve[blockname] = blockdata
            logging.debug('{}, {}, {}'.format(oldblocknumber, blocknumber, blockname))
            continue

        # Reading logic
        if state == "Waiting":
            pass
        elif state == "Read block":
            blockdata.append(line.strip())
    
    for c in curves:
        for blockname, blockparser in blockparsers.items():
            if blockname in c:
                # Remove block from dictionary and parse it
                parsed = blockparser(blockname, c.pop(blockname))
                # now, add new elements from parsed:
                c.update(parsed)

    return curves

def read_dir(directory, mask='*.txt'):
    """ Read all the curves in a given directory """
    import glob
    
    curves = []
    for f in glob.glob(os.path.join(directory, mask)):
        curves += read_htc_file(f)

    return curves

if __name__ == '__main__':
    all_curves = []
    Nfiles = len(sys.argv[1:])
    for f in sys.argv[1:]:
        logging.info(f)
        all_curves += read_htc_file(f)
    for c in all_curves:
        if False and 'Curve Name' in c: 
            logging.debug(c['Curve Name'])
    logging.info('Read {} files, containing {} curves'.format(Nfiles, len(all_curves)))
