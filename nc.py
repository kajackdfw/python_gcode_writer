#!/usr/bin/env python3
import sys
from cattern import Cattern
my_pattern = Cattern(sys.argv[1:])

# Process file
my_pattern.load()
my_pattern.validator()
my_pattern.nc_code_generate()
my_pattern.nc_code_save()
my_pattern.summary_print()
