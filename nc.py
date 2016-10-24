#!/usr/bin/env python
import json
from sys import argv
from pattern import NCPattern



my_pattern = NCPattern('shapeoko_3_xl')
my_pattern.load('patterns/router/vacuum_table_holes.json')
my_pattern.generate_nc_code()
my_pattern.print_summary()
my_pattern.save_nc_data('nc/test.nc')
