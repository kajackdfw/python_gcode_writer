#!/usr/bin/env python
import json
import math
import collections
from sys import argv


# TO DO : outside border should be cut counter-clockwise for routers,
# and clockwise ok for holes/cavities

# Config Settings
# G17 XY Plane
# G18 XZ Plane
# G19 YZ Plane
# G20 Inch mode
# G21 mm mode
# G54 circle mode
# G90 absolute coordinates
# G91 relative mode
# G93
# G94 feed units per minute
# G95 feed rate relative spindle revolutions

# Operations
# G0 Move
# G2 Clockwise Arcs
# G3 Counter-Clockwise Arcs
# M3 Laser ON
# M4 Spindle ON but reverse
# M5 Laser OFF

# ValueError: Expecting property name: line 338 column 7 (char 16779)

class Payload(object):
    def __init__(self, j):
        self.__dict__ = json.loads(j)


def dictionary_to_list( some_dictionary ):
    line_list = []
    for line_number, line_values in some_dictionary.iteritems():
        #line_values['order'] = line_number
        line_list.insert(int(line_values['order']), line_values)
    sorted_lines = sorted(line_list, key=by_order)
    #print sorted_lines
    return sorted_lines


# define the drawing function blocks
def irregular(params, feed_rate):
    nc_lines = "(irregular) \n"
    rel_scale = float(1.0)
    center_x = float(params['x']) * rel_scale
    center_y = float(params['y']) * rel_scale
    if 'relative_points' not in params:
        return ""

    # how many point sets
    points_expected = len(params['relative_points'])
    print "  points expected : ", str(points_expected)

    # create a list of dictionaries , we can sort by the dictionary field order
    line_list = []
    for line_number, line_values in params['relative_points'].iteritems():
        line_values['order'] = line_number
        line_list.insert(int(line_number), line_values)
    one_set_of_lines = sorted(line_list, key=by_order)

    if 'radial_copies' in params and params['radial_copies'] > 1:
        # radial method
        if 'radial_offset' in params:
            radial_offset = math.radians(float(params['radial_offset']))
        else:
            radial_offset = 0.0
        if 'radial_increment' in params:
            radial_increment = math.radians(float(params['radial_increment']))
        elif 'radial_increment' not in params:
            radial_increment = (math.pi * 2.0) / float(params['radial_copies'])
        for radial in range(0, int(params['radial_copies'])):
            azim_adjust = radial * radial_increment + radial_offset
            point_ctr = 1.0
            for line in one_set_of_lines:
                vector_x = (float(line['right']) * rel_scale)
                vector_y = (float(line['up']) * rel_scale)
                hypotenuse = math.sqrt((vector_x * vector_x) + (vector_y * vector_y))
                new_azimuth = math.atan(vector_x / vector_y) + azim_adjust
                new_x = center_x + math.sin(new_azimuth) * hypotenuse
                new_y = center_y + math.cos(new_azimuth) * hypotenuse
                nc_lines += "G01 X{0} Y{1} F{2}\n".format(str3dec(new_x), str3dec(new_y), str3dec(feed_rate))
                if point_ctr == 1:
                    first_x = new_x
                    first_y = new_y
                point_ctr += int(1)
            nc_lines += "G01 X{0} Y{1} F{2}\n".format(str3dec(first_x), str3dec(first_y), str3dec(feed_rate))
        return nc_lines

    # no radial params method
    point_ctr = int(0)
    for line in one_set_of_lines:
        point_ctr += int(1)
        cut_x = float(center_x) + (float(line['right']) * rel_scale)
        cut_y = float(center_y) + (float(line['up']) * rel_scale)
        if point_ctr == 1:
            nc_lines += "M3 \n"
            first_x = cut_x
            first_y = cut_y
        nc_lines += "G01 X" + str3dec(cut_x) + " Y" + str3dec(cut_y) + " F" + str3dec(feed_rate) + " \n"

    if 'close' in params and params['close'] == 'yes':
        nc_lines += "G01 X" + str3dec(first_x) + " Y" + str3dec(first_y) + " F" + str3dec(feed_rate) + " \n"
    nc_lines += "M5 \n"
    return nc_lines


def text(params, feed_rate):
    if len( str(params['text_string'])) > 0:
        nc_lines = "(text \"" + params['text_string'] + "\" )\n"
        start_x = float(params['x'])
        start_y = float(params['y'])
        cursor_x = float(params['x'])
        cursor_y = float(params['y'])

        # text settings
        scale = float(params['height'])
        if params['unit'] == 'mm' and scale <= 10.0 :
            arc_smoothness = math.radians(22.5);
        elif params['unit'] == 'mm':
            arc_smoothness = math.radians(11.25 / 2);
        elif scale <= 0.41:
            arc_smoothness = math.radians(22.5);
        else:
            arc_smoothness = math.radians(11.25 / 2);

        string_length = 0
        for letter in params['text_string']:
            # check if our font supports each letter
            if system_font.chars.has_key( letter ):
                valid_char = letter
            elif system_font.chars.has_key( letter.upper() ):
                valid_char = letter.upper()
            else:
                valid_char = 'undefined'
            # print 'Char :', system_font.chars[ valid_char ]['char']

            stroke_list = dictionary_to_list(system_font.chars[ valid_char ]['strokes'])

            for stroke in stroke_list:
                # print '  ' + stroke['type']
                if stroke['type'] == 'start':
                    cursor_x = start_x + (float(stroke['x']) * scale)
                    cursor_y = start_y + (float(stroke['y']) * scale)
                    nc_lines += 'G00 X' + str3dec(cursor_x) + ' Y' + str3dec(cursor_y) + '\n'
                    nc_lines += 'M3 S125 \n'
                elif stroke['type'] == 'line':
                    cursor_x = start_x + (float(stroke['x']) * scale)
                    cursor_y = start_y + (float(stroke['y']) * scale)
                    nc_lines += 'G01 X' + str3dec(cursor_x) + ' Y' + str3dec(cursor_y) + " F" + str3dec(feed_rate) + "\n"
                elif stroke['type'] == 'arc':
                    cursor_x = start_x + (float(stroke['x']) * scale)
                    cursor_y = start_y + (float(stroke['y']) * scale)
                    radian_start = math.radians(float(stroke['start']))
                    radian_end = math.radians(float(stroke['end']))
                    nc_lines += arc(cursor_x, cursor_y, float(stroke['radius']) * scale, radian_start, radian_end, arc_smoothness, feed_rate)
                elif stroke['type'] == 'move':
                    nc_lines += 'M5 \n'
                    cursor_x = start_x + float(stroke['x']) * scale
                    cursor_y = start_y + float(stroke['y']) * scale
                    nc_lines += 'G00 X' + str3dec(cursor_x) + ' Y' + str3dec(cursor_y) + '\n'
                    nc_lines += 'M3 S125 \n'

            nc_lines += 'M5 \n'
            start_x += float(system_font.chars[ valid_char ]['width']) * scale
            #start_y = start_y
        return nc_lines
    else:
        return "(no text string)";


def arc(x_ctr, y_ctr, radius, start_arc, end_arc, increment, feed_rate):
    corner_lines = "(start arc at " + str(x_ctr) + ", " + str(y_ctr) + ")\n"
    cords = int( ( end_arc - start_arc ) / increment )
    # loop through the arc cords
    for segment in range(1, cords + 1):
        angle = start_arc + (float(segment) * increment)
        x_point = math.sin(angle) * radius + float(x_ctr)
        y_point = math.cos(angle) * radius + float(y_ctr)
        corner_lines += "G01 X" + str3dec(x_point) + " Y" + str3dec(y_point) + " F" + str3dec(feed_rate) + "\n"

    corner_lines += "(end arc)\n"
    return corner_lines


def load_font( font_file_name ):
    font_file = open(font_file_name, 'r')
    font_data = str(font_file.read())
    p = Payload(font_data)
    return p


def circle(params, feed_rate):
    nc_lines = "(circle " + str(params['radius']) + " radius) \n"
    radius = float(params['radius'])
    neg_radius = radius * -1.0

    # circles only need about 6 different numbers
    x = float(params['x'])
    y = float(params['y'])
    left_pt = float(x - radius)
    right_pt = float(x + radius)
    top_pt = float(y + radius)
    bottom_pt = float(y - radius)

    # warm up laser by drawing cross hair
    if cross_hair in params:
        nc_lines += cross_hair(params, feed_rate)
    nc_lines += "G00 X" + str3dec(left_pt) + " Y" + str3dec(y) + " \n"
    nc_lines += "M3 \n"
    nc_lines += "G02 X" + str3dec(x) + " Y" + str3dec(top_pt) + " I" + str3dec(radius) + \
                " J0. F" + str3dec(feed_rate) + "\n"
    nc_lines += "X" + str3dec(right_pt) + " Y" + str3dec(y) + " I0.0 J" + str3dec(neg_radius) + "\n"
    nc_lines += "X" + str3dec(x) + " Y" + str3dec(bottom_pt) + " I" + str3dec(neg_radius) + " J0.0\n"
    nc_lines += "X" + str3dec(left_pt) + " Y" + str3dec(y) + " I0.0 J" + str3dec(radius) + "\n"
    nc_lines += "M5 \n"
    return nc_lines


def polygon(params, feed_rate):
    nc_lines = "(polygon " + str(params['sides']) + " sided) \n"
    radius = float(params['diameter']) / 2.0
    segment_angle = (math.pi * 2.0) / float(params['sides'])
    center_x = float(params['x'])
    center_y = float(params['y'])
    start_x = float(params['x'])
    start_y = float(params['y']) + radius

    nc_lines += "G00 X" + str3dec(start_x) + " Y" + str3dec(start_y) + " Z0.1\n"  # start point
    nc_lines += "G00 Z-1. \n"
    nc_lines += "M3 \n"
    for index in range(1, int(params['sides'])):
        x = center_x + (radius * math.sin(float(index) * segment_angle))
        y = center_y + (radius * math.cos(float(index) * segment_angle))
        nc_lines += "G01 X" + str3dec(x) + " Y" + str3dec(y) + " F" + str3dec(feed_rate) + " \n"

    nc_lines += "G00 X" + str3dec(start_x) + " Y" + str3dec(start_y) + " \n"
    nc_lines += "M5 \n"
    nc_lines += "G01 Z1 \n"
    return nc_lines


def rectangle(params, feed_rate):
    nc_lines = "(rectangle)\n"
    top = float(params['y']) + float(params['tall'])
    right = float(params['x']) + float(params['wide'])
    left = float(params['x'])
    bottom = float(params['y'])
    if 'radius' in params and params['radius'] > 0:
        rad = float(params['radius'])
        nc_lines += "G00 X" + str3dec(left) + " Y" + str3dec(bottom + rad) + " \n"
        nc_lines += "M3\n"
        # left side
        nc_lines += "G01 X" + str3dec(left) + " Y" + str3dec(top - rad) + " F" + str3dec(feed_rate) + "\n"
        nc_lines += corner(left + rad, top - rad, rad, math.pi * 1.5, 4) # upper left corner
        # top
        nc_lines += "G01 X" + str3dec(right - rad) + " Y" + str3dec(top) + " F" + str3dec(feed_rate) + "\n"
        nc_lines += corner(right - rad, top - rad, rad, 0.0, 4)
        # right
        nc_lines += "G01 X" + str3dec(right) + " Y" + str3dec(bottom + rad) + " F" + str3dec(feed_rate) + "\n"
        nc_lines += corner(right - rad, bottom + rad, rad, math.pi / 2.0, 4)
        # bottom
        nc_lines += "G01 X" + str3dec(left + rad) + " Y" + str3dec(bottom) + " F" + str3dec(feed_rate) + "\n"
        nc_lines += corner(left + rad, bottom + rad, rad, math.pi, 4)
        nc_lines += "M5\n"
    else:
        nc_lines = "G00 X" + str3dec(params['x']) + " Y" + str3dec(params['y']) + " F" + str3dec(feed_rate) + "\n"
        nc_lines += "M3\n"
        nc_lines += "G01 X" + str3dec(params['x']) + " Y" + str3dec(
            float(params['y']) + float(params['tall'])) + " F" + str3dec(feed_rate) + "\n"
        nc_lines += "G01 X" + str3dec(float(params['x']) + float(params['wide'])) + " Y" + str3dec(
            float(params['y']) + float(params['tall'])) + " F" + str3dec(feed_rate) + "\n"
        nc_lines += "G01 X" + str3dec(float(params['x']) + float(params['wide'])) + " Y" + str3dec(
                params['y']) + " F" + str3dec(feed_rate) + "\n"
        nc_lines += "G01 X" + str3dec(params['x']) + " Y" + str3dec(params['y']) + " F" + str3dec(feed_rate) + "\n"
        nc_lines += "M5\n"
    return nc_lines


# 90 degree arc for rectangles
def corner(x_ctr, y_ctr, radius, start_rad, cords):
    corner_lines = "(start corner radius at " + str(x_ctr) + ", " + str(y_ctr) + ")\n"
    increment = math.pi / 2 / cords
    # loop through the arc cords
    for segment in range(1, cords + 1):
        angle = start_rad + (float(segment) * increment)
        x_point = math.sin(angle) * radius + float(x_ctr)
        y_point = math.cos(angle) * radius + float(y_ctr)
        corner_lines += "G01 X" + str3dec(x_point) + " Y" + str3dec(y_point) + "\n"

    corner_lines += "(end corner)\n"
    return corner_lines


def cross_hair(params, feed_rate):
    nc_lines = "(cross_hair)\n"
    if 'cross_hair' not in params:
        return nc_lines

    half_a_cross = float(params['cross_hair']) / 2.0
    nc_lines += "G00 X" + str3dec(params['x']) + " Y" + str3dec(float(params['y']) + half_a_cross) + "\n"
    nc_lines += "M3 \n"
    nc_lines += "G00 X" + str3dec(params['x']) + " Y" + str3dec(float(params['y']) - half_a_cross) + "\n"
    nc_lines += "M5 \n"
    nc_lines += "G00 X" + str3dec(float(params['x']) + half_a_cross) + " Y" + str3dec(params['y']) + "\n"
    nc_lines += "M3 \n"
    if params['shape'] != "circle":
        nc_lines += "G00 X" + str3dec(float(params['x']) - half_a_cross) + " Y" + str3dec(params['y']) + "\n"
        nc_lines += "M5 \n"

    return nc_lines


# map the inputs to the function blocks
cut_a_shape = {'circle': circle,
               'cross_hair': cross_hair,
               'irregular': irregular,
               'polygon': polygon,
               'rectangle': rectangle,
               'text': text,
               }


def by_y_then_x(one_cut_with_params):
    y_primary_x_secondary = float(one_cut_with_params['y']) * 1000 + float(one_cut_with_params['x'])
    return y_primary_x_secondary


def by_order(one_item):
    return one_item['order']


def str3dec(float_number_or_string):
    return str(round(float(float_number_or_string), 3))


# ---------------------------------------------------------------------------
# Main program, convert a json array file to a g code nc file
# ---------------------------------------------------------------------------
if len(argv) != 3:
    print "Invalid number of params!"
    print "Try >python json_to_gcode.py input/square_50mm.json output/my_new_file.nc "
    exit()

this_script, input_file, output_file = argv

print "  Json file : ", input_file
print "  Output to : ", output_file
pattern_file = open(input_file, 'r')
nc_file = open(output_file, 'w')
json_array_string = str(pattern_file.read())
json_data_dic = json.loads(json_array_string)
system_font = None

# template for first line of file
nc_first_line = "G17 [unit] G90 G94 G54"

# populate merge fields [xxx] in first line
if json_data_dic['config']['unit'] == 'mm':
    nc_first_line = str.replace(nc_first_line, '[unit]', 'G21')
else:
    nc_first_line = str.replace(nc_first_line, '[unit]', 'G20')

if 'spindle' in json_data_dic['config'] and json_data_dic['config']['spindle'] == 'off':
    spindle_off_or_on = "(M3)\n"
else:
    spindle_off_or_on = "M3 S255 \n"

kerf = float(json_data_dic['config']['tool_diameter']) * 0.5
scale = float(json_data_dic['config']['scale'])

nc_file.write(nc_first_line + "\n")

# create a Python List of Dictionaries we can can sort by values
cut_list = []
for cut_number, cut_values in json_data_dic['interior_cuts'].iteritems():
    cut_list.insert(int(cut_number), cut_values)

sorted_cuts = sorted(cut_list, key=by_y_then_x)

# Loop through the operations
for cut in sorted_cuts:  # json_data_dic['interior_cuts'].iteritems():
    origin_x = float(cut['x'])
    origin_y = float(cut['y'])
    cut['x'] = float(cut['x']) * scale + kerf
    cut['y'] = float(cut['y']) * scale + kerf
    cut['scale'] = scale
    cut['kerf'] = kerf
    if cut['shape'] == 'text' and system_font == None:
        font_file = open('fonts/kajack.json', 'r')
        font_data = str(font_file.read())
        system_font = Payload(font_data)
        cut['unit'] = json_data_dic['config']['unit']
    elif cut['shape'] == 'rectangle':
        cut['wide'] = float(cut['wide']) * scale - kerf - kerf
        cut['tall'] = float(cut['tall']) * scale - kerf - kerf
    elif cut['shape'] == 'circle' and 'diameter' in cut:
        cut['radius'] = float(cut['diameter']) * 0.5 * scale - kerf
    elif cut['shape'] == 'text':
        cut['unit'] = json_data_dic['config']['unit']

    if 'speed' in cut:
        tool_speed = float(cut['speed'])
    else:
        tool_speed = float(json_data_dic['config']['default_speed'])
    # is there an array of this cut ?
    if 'array' not in cut:
        nc_file.write(cut_a_shape[cut['shape']](cut, tool_speed))
    else:
        cutArray = cut['array']  # is there an array of this shape to process ? If not do once in exception
        cut['column_spacing'] = float(cut['array']['x_spacing']) * scale
        cut['row_spacing'] = float(cut['array']['y_spacing']) * scale
        for aCol in range(0, int(cut['array']['columns'])):
            for aRow in range(0, int(cut['array']['rows'])):
                cut_params = {}
                cut_params['x'] = (float(aCol) * cut['column_spacing'] + origin_x) * scale + kerf
                cut_params['y'] = (float(aRow) * cut['row_spacing'] + origin_y) * scale + kerf

                if cut['shape'] == 'rectangle':
                    cut_params['wide'] = cut['wide'] * scale - kerf - kerf
                    cut_params['tall'] = cut['tall'] * scale - kerf - kerf
                elif cut['shape'] == 'circle':
                    cut_params['radius'] = float(float(cut['diameter']) / 2.0) * scale - kerf
                elif cut['shape'] == 'text':
                    cut_params['unit'] = json_data_dic['config']['unit']

                if 'radius' in cut:
                    cut_params['radius'] = float(cut['radius']) * scale - kerf

                nc_file.write(str(cut_a_shape[cut['shape']](cut_params, tool_speed)))

# lastly, prepare to cut the border
if 'speed' in json_data_dic['border']:
    tool_speed = str3dec(json_data_dic['border']['speed'])
else:
    tool_speed = str3dec(json_data_dic['config']['default_speed'])

if 'border' not in json_data_dic or 'shape' not in json_data_dic['border']:
    nc_file.write('(no border found)')
    nc_file.close()

border_params = json_data_dic['border']

# prepare border vars for various shapes
if json_data_dic['border']['shape'] == 'rectangle':
    border_params['wide'] = float(border_params['wide']) * scale + kerf + kerf
    border_params['tall'] = float(border_params['tall']) * scale + kerf + kerf
    border_params['x'] = kerf
    border_params['y'] = kerf
    if 'radius' in json_data_dic['border']:
        border_params['radius'] = float(border_params['radius']) + kerf
    if 'lead_in' in json_data_dic['border']:
        border_params['lead_in'] = float(json_data_dic['border']['lead_in'])
    nc_file.write(str(cut_a_shape[border_params['shape']](border_params, tool_speed)))

if json_data_dic['border']['shape'] == 'circle':
    border_params['radius'] = float(border_params['diameter']) * scale / 2.0 + kerf
    border_params['x'] = border_params['radius'] * scale + kerf
    border_params['y'] = border_params['radius'] * scale + kerf
    if 'lead_in' in json_data_dic['border']:
        border_params['lead_in'] = float(json_data_dic['border']['lead_in'])
    nc_file.write(str(cut_a_shape[border_params['shape']](border_params, tool_speed)))

nc_file.write('(end of script)')
nc_file.close()
print '  File {0} created!'.format(output_file)