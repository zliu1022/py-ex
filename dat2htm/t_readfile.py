# -*- coding: utf-8 -*-
import sys
import numpy as np
import matplotlib.pyplot as plt

if len(sys.argv)!=2:
    print "Usage: "
    print "python readfile.py datfile"
    sys.exit()

in_filename = sys.argv[1]
 
def main():
    print 'try to use several methods to read file:'
    print

    print 'read all into memory1: it\'s better for small file and no EOL'
    with open(in_filename) as input_file:
        lines = input_file.read().splitlines()
    input_file.close()
    print 'total lines:', len(lines)
    print lines[18]
    print

    print 'read all into memory2:'
    in_fd = open(in_filename, 'r')
    try:
        lines = in_fd.readlines()
    finally:
        in_fd.close()
    print 'total lines:', len(lines)
    print 'original:', lines[18]
    print 'replace:', lines[18].replace('\n', '')
    print 'rstrip:', lines[18].rstrip('\n')
    print

    print 'read line by line and deal with it:'
    no = 0
    for line in open(in_filename, 'r'):
        if (no==19): print line
        no += 1
    print 'total lines:', no
    print

    print 'read line by line and deal with it:'
    in_fd  = open(in_filename)
    no = 0
    while 1:
        line = in_fd.readline()
        if not line:
            break
        no += 1
        if (no==19): print line
    print 'total lines:', no

if __name__ == "__main__":
   main()
