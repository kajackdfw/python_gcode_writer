#!/usr/bin/env python3
import json
import sys, getopt
from pattern import NCPattern

def main(argv):
    nc_file = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print ('test.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -m <cnc_machine> -p <pattern_file> -n <nc_file>')
            sys.exit()
        elif opt in ("-m", "--machine"):
            machine = arg
        elif opt in ("-n", "--ncfile"):
            nc_file = arg
        elif opt in ("-p", "--pattern"):
            pattern_file = arg

# Parse the command line arguements
if __name__ == "__main__":
   main(sys.argv[1:])

# Process file
my_pattern = NCPattern('shapeoko_3_xl')
my_pattern.load('patterns/router/vacuum_table_holes.json')
my_pattern.generate_nc_code()
my_pattern.print_summary()
my_pattern.save_nc_data('nc/test.nc')
