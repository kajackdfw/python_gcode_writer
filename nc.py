#!/usr/bin/env python3
import sys
from pattern import NCPattern

# Process file
my_pattern = NCPattern(sys.argv[1:])
my_pattern.load()
my_pattern.generate_nc_code()
my_pattern.save_nc_data()
my_pattern.print_summary()