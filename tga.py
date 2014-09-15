#!/usr/bin/env python

# Author: Carl Sandrock

import sys
import numpy
import pandas
import io

class tga:
    def __init__(self, f):
        """
        Read an file containing tab-delimited blocks and a block of data

        """

        if hasattr(f, 'next'):
            self.filename = f.name
            infile = f
        else:
            self.filename = f
            infile = io.open(f, encoding='utf-16')

        delimiter = '\t'

        # Read header
        self.header = {}
        for line in infile:
            if "StartOfData" in line:
                break
            lineitems = line.strip().split(delimiter)
            if len(lineitems) == 2:
                self.header[lineitems[0]] = lineitems[1]
            else:
                self.header[lineitems[0]] = lineitems[1:]
        else:
            raise

        # Figure out the names of stuff
        Nsig = int(self.header['Nsig'])
        names = [self.header['Sig%i' % (i+1)] for i in range(Nsig)]

        # Read data
        self.data = pandas.read_csv(infile, delimiter=delimiter,
                                    names=names, index_col=0)

    def __repr__(self):
        return "tga('%s')" % self.filename

if __name__ == '__main__':
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    
    filecontents = tga(sys.argv[1])
    pp.pprint(filecontents.header)
    print filecontents.data
