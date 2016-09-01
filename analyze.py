#!/usr/bin/env python
import json
import math
from sys import argv
import gcoder


class Payload(object):
    def __init__(self, j):
        self.__dict__ = json.loads(j)


def dictionary_to_list(some_dictionary):
    line_list = []
    for line_number, line_values in some_dictionary.items():
        line_list.insert(int(line_values['order']), line_values)

    sorted_lines = sorted(line_list, key=by_order)
    return sorted_lines


def by_order(one_item):
    return one_item['order']


def str3dec(float_number_or_string):
    return str(round(float(float_number_or_string), 3))


# ---------------------------------------------------------------------------
# Main program, analyze a json array file
# ---------------------------------------------------------------------------

if len(argv) != 3:
    print("Invalid number of params!")
    print("Try >python analyze.py input/widget.json output/log.txt ")
    exit()

this_script, input_file, output_file = argv

print("  Json file : ", input_file)
print("  Output to : ", output_file)

nc_file = open(output_file, 'w')

pattern_file = open(input_file, 'r')
json_array_string = str(pattern_file.read())
json_data_dic = json.loads(json_array_string)
kerf = float(json_data_dic['config']['tool_diameter']) * 0.5


nc_file.write("G00 X0 Y0 Z \n")


# create a Python List of Dictionaries we can can sort by values
cut_list = []
for cut_number, cut_values in json_data_dic['interior_cuts'].items():
    cut_list.insert(int(cut_number), cut_values)


nc_file.write('(end of script)')
nc_file.close()
print('  File {0} created!'.format(output_file))
