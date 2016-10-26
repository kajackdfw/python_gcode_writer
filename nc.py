#!/usr/bin/env python3
import sys
from pattern import NCPattern
my_pattern = NCPattern(sys.argv[1:])

# Process file
my_pattern.load_pattern()
my_pattern.validate_pattern()
my_pattern.generate_nc_code()
my_pattern.save_nc_data()
my_pattern.print_summary()
