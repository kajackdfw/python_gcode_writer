#!/usr/bin/env python3
import json
import sys, getopt
from pattern import NCPattern

def main(argv):
    command_line_args = []
    command_line_args['nc_file'] = ''
    command_line_args['pattern_file'] = ''
    command_line_args['machine'] = 'shapeoko_3_xl'
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
            command_line_args['machine'] = arg
        elif opt in ("-n", "--ncfile"):
            command_line_args['nc_file'] = arg
        elif opt in ("-p", "--pattern"):
            command_line_args['pattern_file'] = arg
    return command_line_args

# Parse the command line arguements
if __name__ == "__main__":
    args = main(sys.argv[1:])

# Process file
my_pattern = NCPattern(args['machine'])
my_pattern.load(args['pattern_file'])
my_pattern.generate_nc_code()
my_pattern.print_summary()
my_pattern.save_nc_data(args['nc_file'])
