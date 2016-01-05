import json
import math


# TODOS : outside border should be cut counter-clockwise for routers, clockwise ok for holes/cavities

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

# define the function blocks
def circle(params, feed_rate):
    ncLines = "(circle "+ str(params['radius']) +" radius) \n"
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
    if cross_hair in params: ncLines = ncLines + cross_hair( params )
    #ncLines = "G00 X" + str3dec(x) + " Y" + str3dec(y + cross) + " Z0.1\n"
    #ncLines = ncLines + "M3\n"
    #ncLines = ncLines + "G00 Z0.0 F" + str3dec(feed_rate) + "\n"
    #ncLines = ncLines + "G00 X" + str3dec(x) + " Y" + str3dec(y - cross) + " Z0.1\n"
    #ncLines = ncLines + "G00 X" + str3dec(x + cross) + " Y" + str3dec(y) + " Z0.1\n"
    ncLines = ncLines + "G00 X" + str3dec(left_pt) + " Y" + str3dec(y) + " \n"
    ncLines = ncLines + "M3\n"
    ncLines = ncLines + "G02 X" + str3dec(x) + " Y" + str3dec(top_pt) + " I" + str3dec(radius) + " J0. F" + str3dec(feed_rate) + "\n"
    ncLines = ncLines + "X" + str3dec(right_pt) + " Y" + str3dec(y) + " I0.0 J" + str3dec(neg_radius) + "\n"
    ncLines = ncLines + "X" + str3dec(x) + " Y" + str3dec(bottom_pt) + " I" + str3dec(neg_radius) + " J0.0\n"
    ncLines = ncLines + "X" + str3dec(left_pt) + " Y" + str3dec(y) + " I0.0 J" + str3dec(radius) + "\n"
    ncLines = ncLines + "M5\n"
    return ncLines


def polygon(params, feed_rate):
    ncLines = "(polygon "+ str( params['sides'] ) +" sided) \n"
    radius = float(params['diameter']) / 2.0
    segment_angle = (math.pi * 2.0) / float(params['sides'])
    center_x = float(params['x'])
    center_y = float(params['y'])
    start_x = float(params['x'])
    start_y = float(params['y']) + radius

    ncLines = ncLines + "G00 X" + str3dec(start_x) + " Y" + str3dec(start_y) + " Z0.1\n"  # start point
    ncLines = ncLines + "G00 Z-1. \n"
    ncLines = ncLines + "M3\n"
    for index in range(1, int(params['sides'])):
        x = center_x + (radius * math.sin(float(index) * segment_angle))
        y = center_y + (radius * math.cos(float(index) * segment_angle))
        ncLines = ncLines + "G01 X" + str3dec(x) + " Y" + str3dec(y) + " F" + str3dec(feed_rate) + " \n"

    ncLines = ncLines + "G00 X" + str3dec(start_x) + " Y" + str3dec(start_y) + " \n"
    ncLines = ncLines + "M5\n"
    ncLines = ncLines + "G01 Z1\n"
    return ncLines


def rectangle(params, feed_rate):
    ncLines = "(rectangle)\n"
    top = float(params['y']) + float(params['tall'])
    right = float(params['x']) + float(params['wide'])
    left = float(params['x'])
    bottom = float(params['y'])
    if 'radius' in params and params['radius'] > 0:
        rad = float(params['radius'])
        ncLines = ncLines + "G00 X" + str3dec(left) + " Y" + str3dec(bottom + rad) + " \n"
        ncLines = ncLines + "M3\n"
        # left side
        ncLines = ncLines + "G01 X" + str3dec(left) + " Y" + str3dec(top - rad) + " F" + str3dec(feed_rate) + "\n"
        ncLines = ncLines + corner(left + rad, top - rad, rad, math.pi * 1.5, 4)
        # top
        ncLines = ncLines + "G01 X" + str3dec(right - rad) + " Y" + str3dec(top) + " F" + str3dec(feed_rate) + "\n"
        ncLines = ncLines + corner(right - rad, top - rad, rad, 0.0, 4)
        # right
        ncLines = ncLines + "G01 X" + str3dec(right) + " Y" + str3dec(bottom + rad) + " F" + str3dec(feed_rate) + "\n"
        ncLines = ncLines + corner(right - rad, bottom + rad, rad, math.pi / 2.0 , 4)
        # bottom
        ncLines = ncLines + "G01 X" + str3dec(left + rad) + " Y" + str3dec(bottom) + " F" + str3dec(feed_rate) + "\n"
        ncLines = ncLines + corner(left + rad, bottom + rad, rad, math.pi , 4)
        ncLines = ncLines + "M5\n"
    else:
        ncLines = "G00 X" + str3dec(params['x']) + " Y" + str3dec(params['y']) + " F" + str3dec(feed_rate) + "\n"
        ncLines = ncLines + "M3\n"
        ncLines = ncLines + "G01 X" + str3dec(params['x']) + " Y" + str3dec(
            float(params['y']) + float(params['tall'])) + " F" + str3dec(feed_rate) + "\n"
        ncLines = ncLines + "G01 X" + str3dec(float(params['x']) + float(params['wide'])) + " Y" + str3dec(
            float(params['y']) + float(params['tall'])) + " F" + str3dec(feed_rate) + "\n"
        ncLines = ncLines + "G01 X" + str3dec(float(params['x']) + float(params['wide'])) + " Y" + str3dec(
                params['y']) + " F" + str3dec(feed_rate) + "\n"
        ncLines = ncLines + "G01 X" + str3dec(params['x']) + " Y" + str3dec(params['y']) + " F" + str3dec(feed_rate) + "\n"
        ncLines = ncLines + "M5\n"
    return ncLines


def corner(x_ctr, y_ctr, radius, start_rad, segments):
    corner_lines = "(start corner radius at "+ str(x_ctr) +", "+ str(y_ctr) +")\n"
    increment = math.pi / 2 / segments
    # loop through the arc segments
    for segment in range(1, segments + 1):
        angle = start_rad + ( float(segment) * increment )
        x_point = math.sin(angle) * radius + float(x_ctr)
        y_point = math.cos(angle) * radius + float(y_ctr)
        corner_lines = corner_lines +"G01 X"+ str3dec(x_point) +" Y"+ str3dec(y_point) +"\n"

    corner_lines = corner_lines + "(end corner)\n"
    return corner_lines


def cross_hair(params):
    ncLines = "(cross_hair)\n"
    if 'cross_hair' not in params: return ncLines

    half_a_cross = float(params['cross_hair']) / 2.0
    ncLines = ncLines + "G00 X" + str3dec(params['x']) + " Y" + str3dec( float(params['y']) + half_a_cross )
    ncLines = ncLines + "M3 \n"
    ncLines = ncLines + "G00 X" + str3dec(params['x']) + " Y" + str3dec( float(params['y']) - half_a_cross )
    ncLines = ncLines + "M5 \n"
    ncLines = ncLines + "G00 X" + str3dec(float(params['x']) + half_a_cross ) + " Y" + str3dec(params['y'])
    ncLines = ncLines + "M3 \n"
    if params['shape'] != "circle":
        ncLines = ncLines + "G00 X" + str3dec(float(params['x']) - half_a_cross ) + " Y" + str3dec(params['y'])
        ncLines = ncLines + "M5 \n"

    return ncLines


# map the inputs to the function blocks
cutShape = {'circle': circle,
            'polygon': polygon,
            'rectangle': rectangle,
            'cross_hair': cross_hair
            }


def by_Location(cutOpp):
    y_primary_x_secondary = float(cutOpp['y']) * 1000 + float(cutOpp['x'])
    return y_primary_x_secondary


def str3dec(floatNumber):
    return str(round(float(floatNumber), 3))


patternFile = open('input/square_50mm.json', 'r')
ncFile = open('output/square_50mm.nc', 'w')

jstr = str(patternFile.read())
cuttingOps = json.loads(jstr)
ncFileComment = str(cuttingOps)

ncFirstLine = "G17 [unit] G90 G94 G54"

if cuttingOps['config']['unit'] == 'mm':
    ncFirstLine = str.replace(ncFirstLine, '[unit]', 'G21')
else:
    ncFirstLine = str.replace(ncFirstLine, '[unit]', 'G20')

if 'spindle' in cuttingOps['config'] and cuttingOps['config']['spindle'] == 'off':
    spindleOffOn = "(M3)\n"
else:
    spindleOffOn = "M3 \n"

tool_radius = float(cuttingOps['config']['tool_diameter']) * 0.5
scale = float(cuttingOps['config']['scale'])

ncFile.write(ncFirstLine + "\n")
# ncFile.write("(" + str(ncFileComment) + ")\n") This produces a line that overloads the Grbl buffer, but it is handy for debugging in Python

# create a Python List of Dictionaries we can can sort by values
oppList = []
for oppNum, opp in cuttingOps['cut_outs'].iteritems():
    oppList.insert(int(oppNum), opp)

sortedOperations = sorted(oppList, key=by_Location)

# Loop through the operations
for opp in sortedOperations:  # cuttingOps['cut_outs'].iteritems():
    opp['tempX'] = float(opp['x']) * scale
    opp['tempY'] = float(opp['y']) * scale
    if opp['shape'] == 'rectangle': opp['wide'] = float(opp['wide']) * scale ;
    if opp['shape'] == 'rectangle': opp['tall'] = float(opp['tall']) * scale ;
    if opp['shape'] == 'circle': opp['radius'] = float(opp['diameter']) * 0.5 * scale ;
    if 'speed' in opp:
        tool_speed = float(opp['speed'])
    else:
        tool_speed = float(cuttingOps['config']['default_speed'])
    # ncFile.write("G0 F" + cuttingOps['config']['default_speed'] + "\n") # set the current movement speed between cuts
    if 'array' not in opp:
        ncFile.write(cutShape[opp['shape']](opp, tool_speed))
    else:
        cutArray = opp['array']  # is there an array of this shape to process ? If not do once in exception
        opp['column_spacing'] = float(opp['array']['x_spacing']) * scale
        opp['row_spacing'] = float(opp['array']['y_spacing']) * scale
        for aCol in range(0, int(opp['array']['columns'])):
            for aRow in range(0, int(opp['array']['rows'])):
                arrayOpp = {}
                arrayOpp['x'] = float(aCol) * opp['column_spacing'] + opp['tempX']
                arrayOpp['y'] = float(aRow) * opp['row_spacing'] + opp['tempY']
                if (opp['shape'] == 'rectangle'): arrayOpp['wide'] = opp['wide'];
                if (opp['shape'] == 'rectangle'): arrayOpp['tall'] = opp['tall'];
                if (opp['shape'] == 'circle'): arrayOpp['radius'] = float(float(opp['diameter']) / 2.0);
                if 'radius' in opp: arrayOpp['radius'] = float(opp['radius']);
                ncFile.write(str(cutShape[opp['shape']](arrayOpp, tool_speed)))

# cut the border last
nextLine = 'G0 X' + str3dec(tool_radius * -1) + ' Y' + str3dec(tool_radius * -1) + " Z0 F" + cuttingOps['config'][
    'default_speed'] + "\n"
ncFile.write(nextLine)
if 'speed' in cuttingOps['border']:
    tool_speed = str3dec(cuttingOps['border']['speed'])
else:
    tool_speed = str3dec(cuttingOps['config']['default_speed'])

ncFile.write("M3\n")
nextX = str3dec(float(tool_radius * -1))
nextY = str3dec(float(cuttingOps['border']['y']) + tool_radius)
nextLine = "G01 X" + nextX + " Y" + nextY + " F" + tool_speed + "\n"
ncFile.write(nextLine)

nextX = str3dec(float(cuttingOps['border']['x']) + float(tool_radius * -1))
nextLine = "G01 X" + nextX + " Y" + nextY + " \n"
ncFile.write(nextLine)

nextY = str3dec(tool_radius * -1)
nextLine = "G01 X" + nextX + " Y" + nextY + " \n"
ncFile.write(nextLine)

nextX = str3dec(tool_radius * -1)
nextLine = "G01 X" + nextX + " Y" + nextY + " \n"
ncFile.write(nextLine)

ncFile.write("M5\n")

ncFile.write('(end of script)')
ncFile.closed
