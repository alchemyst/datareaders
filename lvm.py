#!/usr/bin/env python

# Author: Carl Sandrock

import sys
import numpy

class lvm:
    def __init__(self, f):
        """
        Read an LVM file as documented in http://www.ni.com/white-paper/4139/en

        Note: Special blocks are ignored.
        """

        if hasattr(f, 'next'):
            self.filename = f.name
            infile = f
        else:
            self.filename = f
            infile = open(f)

        assert infile.next().startswith('LabVIEW Measurement'), "Invalid file"

        # FIXME: This should be read from the header
        delimiter = '\t'

        # Read header
        self.header = {}
        for line in infile:
            if "***End_of_Header***" in line:
                break
            key, value = line.strip().split(delimiter)
            self.header[key] = value
        else:
            raise

        # Read section headers
        self.sectionheader = {}
        for line in infile:
            if not line.strip():
                continue
            if "***End_of_Header***" in line:
                break
            items = line.strip().split(delimiter)
            self.sectionheader[items[0]] = items[1:]
        else:
            raise

        # TODO: Skip special blocks

        # Read data
        # FIXME: This ignores the comment column
        self.data = numpy.recfromtxt(infile, delimiter=delimiter, 
                                     usecols=range(1+int(self.sectionheader['Channels'][0])),
                                     names=True,
                                     dtype=float)

    def __repr__(self):
        return "lvm('%s')" % self.filename

if __name__ == '__main__':
    print lvm(sys.argv[1])
