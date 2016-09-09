#!/usr/bin/env python
import json
import math
from sys import argv


# gcode reference list

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
# G0 Move at travel speed
# G1 Move and cut at feed rate
# G2 Clockwise Arcs
# G3 Counter-Clockwise Arcs
# G4 pause for X seconds

# M2 end program
# M3 Spindle/Laser On
# M4 Spindle ON but reverse
# M5 Spindle/Laser OFF
# M6 T201 ( tool change Grbl, but not TinyG )
# M30 ( end program an rewind/return home )


class Payload(object):
    def __init__(self, j):
        self.__dict__ = json.loads(j)


def dictionary_to_list(some_dictionary):
    line_list = []
    for line_number, line_values in some_dictionary.items():
        line_list.insert(int(line_values['order']), line_values)

    sorted_lines = sorted(line_list, key=by_order)
    return sorted_lines


def rotate_coordinate(x_axis, y_axis, rotation):
    pair = {'x': x_axis, 'y': y_axis}

    if x_axis == 0 and y_axis == 0:
        return pair
    elif x_axis == 0 and y_axis > 0:
        azim = math.radians(rotation)
        hypot = y_axis
    elif x_axis == 0 and y_axis < 0:
        azim = math.pi + math.radians(rotation)
        hypot = abs(y_axis)
    elif x_axis > 0 and y_axis == 0:
        azim = math.pi / 2.0 + math.radians(rotation)
        hypot = abs(x_axis)
    elif x_axis < 0 and y_axis == 0:
        azim = math.pi * 1.5 + math.radians(rotation)
        hypot = abs(x_axis)
    elif y_axis < 0:
        azim = math.pi - math.atan(x_axis / abs(y_axis)) + math.radians(rotation)
        hypot = math.sqrt(abs(x_axis) * abs(x_axis) + abs(y_axis) * abs(y_axis))
    else:
        azim = math.atan(x_axis / y_axis) + math.radians(rotation)
        hypot = math.sqrt(abs(x_axis) * abs(x_axis) + abs(y_axis) * abs(y_axis))

    pair['x'] = math.sin(azim) * hypot
    pair['y'] = math.cos(azim) * hypot
    return pair


# draw some lines, one line, one set of lines, or radial copies of lines
def lines(params, feed_rate):
    rel_scale = float(1.0)
    center_x = float(params['x']) * rel_scale
    center_y = float(params['y']) * rel_scale
    if 'relative_points' not in params:
        return ""

    # create a list of dictionaries , we can sort by the dictionary field order
    line_list = []
    for line_number, line_values in params['relative_points'].items():
        line_values['order'] = line_number
        line_list.insert(int(line_number), line_values)
    one_set_of_lines = sorted(line_list, key=by_order)
    radial_count = 1

    if 'radial_copies' in params and int(params['radial_copies']) > 0:
        nc_lines = '( radial copies centered at X' + str3dec(center_x) + ', Y' + str3dec(center_y) + ' ) \n'

        if 'radial_offset' in params:
            radial_offset = math.radians(float(params['radial_offset']))
        else:
            radial_offset = 0.0

        if 'radial_increment' in params:
            radial_increment = math.radians(float(params['radial_increment']))
        else:
            radial_increment = (math.pi * 2.0) / float(params['radial_copies'])

        for radial in range(0, int(params['radial_copies'])):
            azim_adjust = radial * radial_increment + radial_offset
            point_ctr = 1.0
            for line in one_set_of_lines:
                vector_x = (float(line['x_offset']) * rel_scale)
                vector_y = (float(line['y_offset']) * rel_scale)
                hypotenuse = math.sqrt((vector_x * vector_x) + (vector_y * vector_y))
                new_azimuth = math.atan(vector_x / vector_y) + azim_adjust
                new_x = center_x + math.sin(new_azimuth) * hypotenuse
                new_y = center_y + math.cos(new_azimuth) * hypotenuse
                if point_ctr == 1 and 'close_links' in params and params['close_links'] == 'TRUE':
                    nc_lines += "M5 \n"
                    nc_lines += "G00 X{0} Y{1} F{2} (first link and chain start)\n".format(str3dec(new_x), str3dec(new_y), str3dec(feed_rate))
                    nc_lines += "M3 S" + str3dec(params['spindle_speed']) + " \n"
                    nc_lines += "G01 X{0} Y{1} F{2}\n".format(str3dec(new_x), str3dec(new_y), str3dec(feed_rate))
                    link_start_x = new_x
                    link_start_y = new_y
                    original_x = new_x
                    original_y = new_y
                elif point_ctr == 1 and radial_count == 1 and 'close_chain' in params and params['close_chain'] == 'TRUE':
                    nc_lines += "M5 \n"
                    nc_lines += "G00 X{0} Y{1} F{2} (first link and chain start)\n".format(str3dec(new_x), str3dec(new_y), str3dec(feed_rate))
                    nc_lines += "M3 S" + str3dec(params['spindle_speed']) + " \n"
                    original_x = new_x
                    original_y = new_y
                elif 'radius' in line:
                    arc_smoothness = math.radians(11.25 / 2)  # this should not be hard coded
                    radian_start = math.radians(float(line['start'])) + azim_adjust
                    radian_end = math.radians(float(line['end'])) + azim_adjust
                    nc_lines += arc_2d(new_x, new_y, float(line['radius']), radian_start, radian_end, arc_smoothness, str3dec(feed_rate))
                    print(' Arc new_x = ' + str(new_x))
                    print('     new_y = ' + str(new_y))
                    print('     radian_start = ' + str(radian_start))
                    print('     radian_end = ' + str(radian_end))
                    print('     new_x = ' + str(new_x))
                    print('     new_y = ' + str(new_y))
                else:
                    nc_lines += "G01 X{0} Y{1} F{2}\n".format(str3dec(new_x), str3dec(new_y), str3dec(feed_rate))

                # last instruction in line loop
                point_ctr += int(1)

            if 'close_links' in params and params['close_links'] == 'TRUE':
                nc_lines += "G01 X{0} Y{1} F{2} (close link)\n".format(str3dec(link_start_x), str3dec(link_start_y), str3dec(feed_rate))
                nc_lines += "M5 \n"
            elif 'close_chain' in params and params['close_chain'] != 'TRUE':
                nc_lines += "M5 \n"

            radial_count += int(1)

        # just exited the radial loop and do ?
        if 'close_chain' in params and params['close_chain'] == 'TRUE':
            nc_lines += "G01 X{0} Y{1} F{2} (close chain)\n".format(str3dec(original_x), str3dec(original_y), str3dec(feed_rate))

        nc_lines += "M5 \n"
        return nc_lines

    # no radial params method
    point_ctr = int(0)
    nc_lines = '( lines relative to X' + str3dec(center_x) + ', Y' + str3dec(center_y) + ' ) \n'
    for line in one_set_of_lines:
        point_ctr += int(1)
        cut_x = float(center_x) + (float(line['x_offset']) * rel_scale)
        cut_y = float(center_y) + (float(line['y_offset']) * rel_scale)
        if 'z' in line:
            z_move = ' Z' + str3dec(line['z'])
        else:
            z_move = ''

        if point_ctr == 1:
            first_x = cut_x
            first_y = cut_y
            nc_lines += "M5 \n"
            nc_lines += "G00 X" + str3dec(cut_x) + " Y" + str3dec(cut_y) + z_move + " F" + str3dec(feed_rate) + " \n"
            nc_lines += "M3 S" + str3dec(params['spindle_speed']) + " \n"
        elif 'radius' in line:
            arc_smoothness = math.radians(11.25 / 2)  # this should not be hard coded
            radian_start = math.radians(float(line['start']))
            radian_end = math.radians(float(line['end']))
            nc_lines += arc_2d(cut_x, cut_y, float(line['radius']), radian_start, radian_end, arc_smoothness, feed_rate)
        else:
            nc_lines += "G01 X" + str3dec(cut_x) + " Y" + str3dec(cut_y) + z_move + " F" + str3dec(feed_rate) + " \n"

    if 'close_links' in params and params['close_links'] == 'TRUE':
        nc_lines += "G01 X" + str3dec(first_x) + " Y" + str3dec(first_y) + " F" + str3dec(feed_rate) + " \n"

    nc_lines += "M5 \n"
    return nc_lines


def text(params, feed_rate):
    if len(str(params['text_string'])) > 0:
        nc_lines = "(text \"" + params['text_string'] + "\" )\n"
        start_x = float(params['x'])
        start_y = float(params['y'])

        # set some neede values if not provided
        if 'spindle_speed' not in params:
            params['spindle_speed'] = 255.0

        if 'surface' in params:
            surface = float(params['surface'])
        else:
            surface = 0.00

        z_depth = surface - (float(params['height']) * 0.05)
        pen_up = surface + (float(params['height']) * 0.05)

        # text settings
        text_scale = float(params['height'])
        if 'unit' in params and params['unit'] == 'mm' and text_scale <= 10.0:
            arc_smoothness = math.radians(22.5)
        elif 'unit' in params and params['unit'] == 'mm':
            arc_smoothness = math.radians(11.25 / 2)
        elif text_scale <= 0.41:
            arc_smoothness = math.radians(22.5)
        else:
            arc_smoothness = math.radians(11.25 / 2)

        # text rotation ?
        if 'rotate' not in params or ('rotate' in params and float(params['rotate']) == 0):
            params['rotate'] = 0.0
        else:
            params['rotate'] = float(params['rotate'])

        # Start processing the string
        for letter in params['text_string']:
            # check if our font supports each letter
            if letter in system_font.chars:
                supported_char = letter
            elif letter.upper() in system_font.chars:
                supported_char = letter.upper()
            else:
                supported_char = 'undefined'

            # get ready to start drawing a letter
            stroke_list = dictionary_to_list(system_font.chars[supported_char]['strokes'])
            for stroke in stroke_list:
                # print '  ' + stroke['type']

                # rotate x and y
                if 'rotate' in params and params['rotate'] != 0:
                    new_coordinate = rotate_coordinate(float(stroke['x']), float(stroke['y']), params['rotate'])
                    rotated_x = new_coordinate['x']
                    rotated_y = new_coordinate['y']
                    rotate_arc = math.radians(params['rotate'])
                else:
                    rotate_arc = 0.0
                    rotated_x = stroke['x']
                    rotated_y = stroke['y']

                if stroke['type'] == 'start':
                    cursor_x = start_x + (float(rotated_x) * text_scale)
                    cursor_y = start_y + (float(rotated_y) * text_scale)
                    nc_lines += 'G00 Z' + str3dec(params['ceiling']) + ' \n'
                    nc_lines += 'G00 X' + str3dec(cursor_x) + ' Y' + str3dec(cursor_y) + '\n'
                    nc_lines += 'M3 S' + str3dec(params['spindle_speed']) + ' \n'
                    nc_lines += 'G01 Z' + str3dec(z_depth) + ' F' + str3dec(feed_rate / 2) + ' \n'
                elif stroke['type'] == 'line':
                    cursor_x = start_x + (float(rotated_x) * text_scale)
                    cursor_y = start_y + (float(rotated_y) * text_scale)
                    nc_lines += 'G01 X' + str3dec(cursor_x) + ' Y' + str3dec(cursor_y) + " F" + str3dec(feed_rate) + "\n"
                elif stroke['type'] == 'arc':
                    cursor_x = start_x + (float(rotated_x) * text_scale)
                    cursor_y = start_y + (float(rotated_y) * text_scale)
                    radian_start = math.radians(float(stroke['start'])) + rotate_arc
                    radian_end = math.radians(float(stroke['end'])) + rotate_arc
                    nc_lines += arc_2d(cursor_x, cursor_y, float(stroke['radius']) * text_scale, radian_start, radian_end, arc_smoothness, feed_rate)
                elif stroke['type'] == 'move':
                    nc_lines += 'G00 Z' + str3dec(pen_up) + ' \n'
                    nc_lines += 'M5 \n'
                    cursor_x = start_x + float(rotated_x) * text_scale
                    cursor_y = start_y + float(rotated_y) * text_scale
                    nc_lines += 'G00 X' + str3dec(cursor_x) + ' Y' + str3dec(cursor_y) + '\n'
                    nc_lines += 'M3 S' + str3dec(params['spindle_speed']) + ' \n'
                    nc_lines += 'G01 Z' + str3dec(z_depth) + ' \n'

            nc_lines += 'M5 \n'
            nc_lines += "G00 Z" + str3dec(float(params['ceiling']))
            if params['rotate'] == 0:
                start_x += float(system_font.chars[supported_char]['width']) * text_scale
                # start_y = start_y
            else:
                start_x += float(system_font.chars[supported_char]['width']) * text_scale * math.sin(math.radians(90.0+params['rotate']))
                start_y += float(system_font.chars[supported_char]['width']) * text_scale * math.cos(math.radians(90.0+params['rotate']))

        return nc_lines
    else:
        return "(no text string)"


# this is not a normal shape operation, it is a sub task / helper for other shapes or text
def arc_2d(x_ctr, y_ctr, radius, start_arc, end_arc, increment, feed_rate):
    corner_lines = ""
    cords = int((end_arc - start_arc) / increment)

    if start_arc > end_arc:
        # Counter clockwise arc!!
        cords = abs(cords)
        increment *= -1.0

    for segment in range(1, cords + 1):
        angle = start_arc + (float(segment) * increment)
        x_point = math.sin(angle) * radius + float(x_ctr)
        y_point = math.cos(angle) * radius + float(y_ctr)
        corner_lines += "G01 X" + str3dec(x_point) + " Y" + str3dec(y_point) + " F" + str3dec(feed_rate) + "\n"

    return corner_lines


def arc(params, feed_rate):
    arc_lines = "(center arc at " + str(params['x']) + ", " + str(params['y']) + ")\n"
    cords = int((params['end'] - params['start']) / params['increment'])
    if params['start'] > params['end']:
        # Counter clockwise arc!!
        cords = abs(cords)
        params['increment'] *= -1.0

    arc_lines += '(  cords = ' + str(cords) + ') \n'
    arc_lines += '(  params_increment = ' + str(params['increment']) + ') \n'

    first_x = math.sin(params['start']) * params['radius'] + params['x']
    first_y = math.cos(params['start']) * params['radius'] + params['y']
    arc_lines += "M5 \n"
    arc_lines += "G00 X" + str3dec(first_x) + " Y" + str3dec(first_y) + " \n"
    arc_lines += "M3 S" + str3dec(params['spindle_speed']) + " \n"

    for segment in range(1, cords):
        angle = params['start'] + (float(segment) * params['increment'])
        x_point = math.sin(angle) * params['radius'] + params['x']
        y_point = math.cos(angle) * params['radius'] + params['y']
        arc_lines += "G01 X" + str3dec(x_point) + " Y" + str3dec(y_point) + " F" + str3dec(feed_rate) + "\n"

    last_x = math.sin(params['end']) * params['radius'] + params['x']
    last_y = math.cos(params['end']) * params['radius'] + params['y']
    arc_lines += "G01 X" + str3dec(last_x) + " Y" + str3dec(last_y) + " F" + str3dec(feed_rate)
    arc_lines += 'M5 \n'
    arc_lines += "(end arc)\n"
    return arc_lines


def circle(params, feed_rate):
    nc_lines = "(circle " + str(params['radius']) + " radius) \n"
    radius = float(params['radius'])

    # circles only need about 6 different numbers
    x = float(params['x'])
    y = float(params['y'])

    # warm up laser by drawing cross hair
    if cross_hair in params:
        nc_lines += cross_hair(params, feed_rate)
    nc_lines += "G00 X" + str3dec(x) + " Y" + str3dec(y + radius) + " \n"
    nc_lines += "M3 S" + str3dec(params['spindle_speed']) + " \n"

    smoothness = 11.25
    nc_lines += arc_2d(x, y, radius, 0, math.radians(360), math.radians(smoothness), feed_rate)
    nc_lines += "M5 \n"
    return nc_lines


def drill(params, feed_rate):
    nc_lines = "(drill " + str(params['diameter']) + " hole) \n"
    nc_lines += "G00 X" + str3dec(params['x']) + " Y" + str3dec(params['y']) + " Z" + str3dec(float(params['ceiling'])) + "\n"

    if (abs(params['bottom']) + 0.0625) > params['stock_depth']:
        params['bottom'] = (params['stock_depth'] + 0.0625) * -1

    # drill a center hole
    nc_lines += "M3 S" + str3dec(params['spindle_speed']) + " \n"
    nc_lines += "G01 X" + str3dec(params['x']) + " Y" + str3dec(params['y']) + " Z0.00 F" + str3dec(feed_rate / 2.0) + " \n"
    nc_lines += "G01 X" + str3dec(params['x']) + " Y" + str3dec(params['y']) + " Z" + str3dec(float(params['bottom'])) + " F" + str3dec(feed_rate / 2.0) + " \n"
    nc_lines += "G01 X" + str3dec(params['x']) + " Y" + str3dec(params['y']) + " Z" + str3dec(float(params['ceiling'])) + " F" + str3dec(feed_rate / 2.0) + " \n"

    # if the hole is bigger than the tool then start a helical pattern
    if params['diameter'] > params['tool_diameter']:
        removal_radius = (params['diameter'] / 2.0) - (params['tool_diameter'] / 2) - params['finish_cut']

        # create a straight down start hole
        nc_lines += "G01 X" + str3dec(params['x']) + " Y" + str3dec(params['y'] + removal_radius) + \
                    " Z" + str3dec(float(params['ceiling'])) + " F" + str3dec(feed_rate) + "\n"
        nc_lines += "G01 X" + str3dec(params['x']) + " Y" + str3dec(params['y'] + removal_radius) + \
                    " Z" + str3dec(float(params['bottom'])) + " F" + str3dec(feed_rate / 3.0) + " (start hole)\n"
        nc_lines += "G01 X" + str3dec(params['x']) + " Y" + str3dec(params['y'] + removal_radius) + \
                    " Z0.00 F" + str3dec(feed_rate) + "\n"

        # calculate depth steps
        start_z = 0.0
        increment = math.pi * (1.0 / (params['diameter'] * 10.0))
        step_count = math.ceil(abs(params['bottom']) / 0.1) * -1
        step_down = params['bottom'] / float(step_count)
        nc_lines += "(step down = " + str3dec(step_down) + ")"
        step_radius = params['tool_diameter'] / 3

        # cut a shallow guide trough
        while start_z > params['bottom']:
            current_radius = removal_radius
            if params['stock_depth'] > abs(params['bottom']) + 0.0625:
                while current_radius > (params['tool_diameter'] / 2):
                    nc_lines += "G01 X" + str3dec(params['x']) + " Y" + str3dec(params['y'] + current_radius) + \
                            " Z" + str3dec(start_z) + " F" + str3dec(feed_rate / 2.0) + "(plunge)\n"
                    nc_lines += arc_2d(params['x'], params['y'], current_radius, 0.0, math.pi * -2.1, increment, feed_rate)
                    current_radius -= step_radius

            else:
                nc_lines += "G01 X" + str3dec(params['x']) + " Y" + str3dec(params['y'] + current_radius) + \
                            " Z" + str3dec(start_z) + " F" + str3dec(feed_rate / 2.0) + "(plunge)\n"
                nc_lines += arc_2d(params['x'], params['y'], current_radius, 0.0, math.pi * 2.1, increment, feed_rate)
            start_z -= step_down

        # do the bottom of the circle, it might have been omitted previously because of rounding
        if params['stock_depth'] > abs(params['bottom']) + 0.0625:
            current_radius = removal_radius
            nc_lines += "G01 X" + str3dec(params['x']) + " Y" + str3dec(params['y'] + current_radius) + " \n"
            nc_lines += "G01 Z" + str3dec(start_z) + " F" + str3dec(feed_rate / 2) + " \n"
            while current_radius > (params['tool_diameter'] / 2):
                nc_lines += arc_2d(params['x'], params['y'], current_radius, 0.0, math.pi * -2.1, increment, feed_rate)
                current_radius -= step_radius
        else:
            nc_lines += "G01 X" + str3dec(params['x']) + " Y" + str3dec(params['y'] + removal_radius) + \
                        " Z" + str3dec(params['bottom']) + " F" + str3dec(feed_rate / 2.0) + " \n"
            nc_lines += arc_2d(params['x'], params['y'], removal_radius, 0.0, math.pi * 2.1, increment, feed_rate)

        # finish cut
        nc_lines += '(finish cut)\n'
        nc_lines += "G01 X" + str3dec(params['x']) + " Y" + str3dec(params['y'] + (params['diameter'] / 2.0) - (params['tool_diameter'] / 2)) + \
                    " Z" + str3dec(params['bottom']) + " F" + str3dec(feed_rate / 2.0) + " \n"
        nc_lines += arc_2d(params['x'], params['y'], ((params['diameter'] / 2.0) - (params['tool_diameter'] / 2)), 0.0, math.pi * 6.2, increment, feed_rate / 2.0)

    nc_lines += "G01 Z" + str3dec(params['ceiling']) + " F" + str3dec(feed_rate) + " \n"
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
    nc_lines += "M3 S" + params['spindle_speed'] + " \n"
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

    if 'spindle_speed' not in params:
        params['spindle_speed'] = 255.0

    if 'radius' in params and params['radius'] > 0:
        rad = float(params['radius'])
        nc_lines += "G00 X" + str3dec(left) + " Y" + str3dec(bottom + rad) + " \n"
        nc_lines += "M3 S" + str(params['spindle_speed']) + " \n"
        # left side
        nc_lines += "G01 X" + str3dec(left) + " Y" + str3dec(top - rad) + " F" + str3dec(feed_rate) + "\n"
        nc_lines += corner(left + rad, top - rad, rad, math.pi * 1.5, 4)  # upper left corner
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
        nc_lines += "M3 S" + str3dec(params['spindle_speed']) + " \n"
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
    nc_lines += "M5 \n"
    nc_lines += "G00 X" + str3dec(params['x']) + " Y" + str3dec(float(params['y']) + half_a_cross) + "\n"
    nc_lines += "M3 S" + str3dec(params['spindle_speed']) + " \n"
    nc_lines += "G01 X" + str3dec(params['x']) + " Y" + str3dec(float(params['y']) - half_a_cross) + " F" + str3dec(feed_rate) + " \n"
    nc_lines += "M5 \n"
    nc_lines += "G00 X" + str3dec(float(params['x']) + half_a_cross) + " Y" + str3dec(params['y']) + "\n"
    nc_lines += "M3 S" + str3dec(params['spindle_speed']) + " \n"
    nc_lines += "G01 X" + str3dec(float(params['x']) - half_a_cross) + " Y" + str3dec(params['y']) + " F" + str3dec(feed_rate) + "\n"
    nc_lines += "M5 \n"
    return nc_lines


def by_y_then_x(one_cut_with_params):
    y_primary_x_secondary = float(one_cut_with_params['y']) * 1000 + float(one_cut_with_params['x'])
    return y_primary_x_secondary


def by_order(one_item):
    return one_item['order']


def str3dec(float_number_or_string):
    return str(round(float(float_number_or_string), 3))


# map the supported cut methods to the function blocks
cut_a_shape = {'circle': circle,
               'cross_hair': cross_hair,
               'drill': drill,
               'lines': lines,
               'polygon': polygon,
               'rectangle': rectangle,
               'text': text,
               'arc': arc
               }


# ---------------------------------------------------------------------------
# Main program, convert a json array file to a g code nc file
# ---------------------------------------------------------------------------

if len(argv) != 3:
    print("Invalid number of params!")
    print("Try >python json_to_gcode.py input/square_50mm.json output/my_new_file.nc ")
    exit()

this_script, input_file, output_file = argv

print("  Json file : ", input_file)
print("  Output to : ", output_file)

nc_file = open(output_file, 'w')

pattern_file = open(input_file, 'r')
json_array_string = str(pattern_file.read())
json_data_dic = json.loads(json_array_string)

system_font = None

# template for first line of file
nc_first_line = "G17 [unit] G90 G94 G54"

# populate merge fields [xxx] in first line
if 'unit' in json_data_dic and json_data_dic['config']['unit'] == 'mm':
    nc_first_line = str.replace(nc_first_line, '[unit]', 'G21')
else:
    nc_first_line = str.replace(nc_first_line, '[unit]', 'G20')

# set some default values
if 'spindle_speed' in json_data_dic['config']:
    default_spindle_speed = float(json_data_dic['config']['spindle_speed'])
else:
    default_spindle_speed = 255.0

if 'speed' in json_data_dic['config']:
    default_speed = float(json_data_dic['config']['speed'])
else:
    default_speed = 255.0

if 'retract_spindle_to' in json_data_dic['config']:
    default_ceiling = float(json_data_dic['config']['retract_spindle_to'])
else:
    default_ceiling = 0.5

if 'scale' in json_data_dic['config']:
    scale = float(json_data_dic['config']['scale'])
else:
    scale = 1.000

if 'finish_cut' in json_data_dic['config']:
    finish_cut = float(json_data_dic['config']['finish_cut'])
elif json_data_dic['config']['unit'] == 'mm':
    finish_cut = 1.000
else:
    finish_cut = 0.031

if 'stock_depth' in json_data_dic['config']:
    stock_depth = float(json_data_dic['config']['stock_depth'])
else:
    stock_depth = 0.1

kerf = float(json_data_dic['config']['tool_diameter']) * 0.5


nc_file.write(nc_first_line + "\n")
nc_file.write('G00 X0 Y0 Z' + str3dec(default_ceiling) + "\n")


# create a Python List of Dictionaries we can can sort by values
cut_list = []
for cut_number, cut_values in json_data_dic['interior_cuts'].items():
    cut_list.insert(int(cut_number), cut_values)

if 'sorted' in json_data_dic['config'] and json_data_dic['config']['sorted'] == 'yx':
    sorted_cuts = sorted(cut_list, key=by_y_then_x)
else:
    sorted_cuts = cut_list

# Loop through the operations
for cut in sorted_cuts:
    origin_x = float(cut['x'])
    origin_y = float(cut['y'])
    cut['x'] = float(cut['x']) * scale + kerf
    cut['y'] = float(cut['y']) * scale + kerf
    cut['scale'] = scale
    cut['kerf'] = kerf
    cut['ceiling'] = float(default_ceiling)
    if cut['shape'] == 'text' and system_font is None:
        font_file = open('fonts/' + cut['font'] + '.json', 'r')
        font_data = str(font_file.read())
        system_font = Payload(font_data)
        cut['unit'] = json_data_dic['config']['unit']
    elif cut['shape'] == 'rectangle':
        cut['wide'] = float(cut['wide']) * scale - kerf - kerf
        cut['tall'] = float(cut['tall']) * scale - kerf - kerf
    elif cut['shape'] == 'circle' and 'diameter' in cut:
        cut['radius'] = float(cut['diameter']) * 0.5 * scale - kerf
    elif cut['shape'] == 'arc':
        # adjust and typecast vars
        cut['x'] = float(cut['x']) * scale + kerf
        cut['y'] = float(cut['y']) * scale + kerf
        cut['radius'] = float(cut['radius']) * scale
        cut['start'] = math.radians(float(cut['start']))
        cut['end'] = math.radians(float(cut['end']))
        cut['increment'] = math.radians(float(cut['increment']))
    elif cut['shape'] == 'lines':
        cut['x'] = float(cut['x']) * scale + kerf
        cut['y'] = float(cut['y']) * scale + kerf
    elif cut['shape'] == 'drill':
        cut['x'] = float(cut['x']) * scale + kerf
        cut['y'] = float(cut['y']) * scale + kerf
        cut['tool_diameter'] = float(json_data_dic['config']['tool_diameter'])
        cut['diameter'] = float(cut['diameter'])
        cut['scale'] = scale
        cut['finish_cut'] = finish_cut
        cut['stock_depth'] = stock_depth
        if 'depth' in cut:
            cut['bottom'] = 0.0 - float(cut['depth'])
        elif 'bottom' in cut:
            cut['bottom'] = float(cut['bottom'])
        else:
            cut['bottom'] = 0.0 - stock_depth

    if 'feed_rate' in cut:
        tool_feed_rate = float(cut['feed_rate'])
    else:
        tool_feed_rate = float(json_data_dic['config']['default_feed_rate'])

    if 'spindle_speed' in cut:
        cut['spindle_speed'] = float(cut['spindle_speed'])
    else:
        cut['spindle_speed'] = default_spindle_speed

    # is there an array of this cut ?
    if 'array' not in cut:
        nc_file.write(cut_a_shape[cut['shape']](cut, tool_feed_rate))
    else:
        cutArray = cut['array']  # is there an array of this shape to process ? If not do once in exception
        cut['column_spacing'] = float(cut['array']['x_spacing']) * scale
        cut['row_spacing'] = float(cut['array']['y_spacing']) * scale
        for aCol in range(0, int(cut['array']['columns'])):
            for aRow in range(0, int(cut['array']['rows'])):
                cut_params = {}
                cut_params['x'] = (float(aCol) * cut['column_spacing'] + origin_x) * scale + kerf
                cut_params['y'] = (float(aRow) * cut['row_spacing'] + origin_y) * scale + kerf
                cut_params['spindle_speed'] = cut['spindle_speed']
                cut_params['ceiling'] = float(default_ceiling)

                # pass the necessary attributes for completing the cut
                if cut['shape'] == 'rectangle':
                    cut_params['wide'] = cut['wide'] * scale - kerf - kerf
                    cut_params['tall'] = cut['tall'] * scale - kerf - kerf
                elif cut['shape'] == 'circle' and 'diameter' in cut:
                    cut_params['radius'] = float(float(cut['diameter']) / 2.0) * scale - kerf
                elif cut['shape'] == 'circle':
                    cut_params['radius'] = float(cut['radius']) * scale - kerf
                elif cut['shape'] == 'arc':
                    cut_params['radius'] = float(cut['radius']) * scale
                elif cut['shape'] == 'text':
                    cut_params['unit'] = json_data_dic['config']['unit']
                elif cut['shape'] == 'drill':
                    cut_params['diameter'] = float(cut['diameter'])
                    cut_params['bottom'] = float(cut['bottom'])
                    cut_params['tool_diameter'] = float(json_data_dic['config']['tool_diameter'])
                    cut_params['scale'] = scale
                    cut_params['finish_cut'] = finish_cut
                    cut_params['ceiling'] = float(default_ceiling)
                    cut_params['stock_depth'] = stock_depth

                if 'radius' in cut:
                    cut_params['radius'] = float(cut['radius']) * scale - kerf

                nc_file.write(str(cut_a_shape[cut['shape']](cut_params, tool_feed_rate)))

# lastly, prepare to cut the border
if 'feed_rate' in json_data_dic['border']:
    tool_feed_rate = str3dec(json_data_dic['border']['feed_rate'])
else:
    tool_feed_rate = str3dec(json_data_dic['config']['default_feed_rate'])

if 'border' not in json_data_dic or 'shape' not in json_data_dic['border']:
    nc_file.write('(no border found)')
    nc_file.close()

border_params = json_data_dic['border']
if 'spindle_speed' not in border_params:
    border_params['spindle_speed'] = default_spindle_speed

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
    nc_file.write("(rectangular border) \n")
    nc_file.write(str(cut_a_shape[border_params['shape']](border_params, tool_feed_rate)))

if json_data_dic['border']['shape'] == 'circle':
    border_params['radius'] = float(border_params['diameter']) * scale / 2.0 + kerf
    border_params['x'] = border_params['radius'] * scale + kerf
    border_params['y'] = border_params['radius'] * scale + kerf
    if 'lead_in' in json_data_dic['border']:
        border_params['lead_in'] = float(json_data_dic['border']['lead_in'])
    nc_file.write("(circular border) \n")
    nc_file.write(str(cut_a_shape[border_params['shape']](border_params, tool_feed_rate)))

nc_file.write('M5 \n')
nc_file.write('G00 X0 Y0 \n')
nc_file.write('(end of script)')
nc_file.close()
print('  File {0} created!'.format(output_file))
