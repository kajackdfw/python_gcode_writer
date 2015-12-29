import json

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
def circle( params, feedRate ):
    radius = float(params['radius'])
    negRadius = radius * -1.0

    #circles only need about 6 different numbers
    x = float(params['x'])
    y = float(params['y'])
    leftPt   = float( x - radius )
    rightPt  = float( x + radius )
    topPt    = float( y + radius )
    bottomPt = float( y - radius )

    ncLines = "G00 X" + str3dec(leftPt) + " Y" + str3dec(y) + " Z0.1\n"
    ncLines = ncLines + "G01 Z0.0\n"
    ncLines = ncLines + "M3\n"
    ncLines = ncLines + "G02 X" + str3dec(x)       + " Y" + str3dec(topPt)      + " I" + str3dec(radius)    + " J0. F" + str3dec(feedRate) + "\n"
    ncLines = ncLines +     "X" + str3dec(rightPt) + " Y" + str3dec(y)          + " I0.0 J"             + str3dec( negRadius ) + "\n"
    ncLines = ncLines +     "X" + str3dec(x)       + " Y" + str3dec( bottomPt ) + " I" + str3dec(negRadius) + " J0.0\n"
    ncLines = ncLines +     "X" + str3dec(leftPt)  + " Y" + str3dec(y)          + " I0.0 J"             + str3dec( radius ) + "\n"
    ncLines = ncLines + "M5\n"

    return ncLines


def polygon( params, feedRate ):
    radius = float(params['radius'])


    #circles only need about 6 different numbers
    x = float(params['x'])
    y = float(params['y'])


    ncLines = "G0 X" + str3dec(x) + " Y" + str3dec(y) + " Z0.1\n"

    ncLines = ncLines + "M3\n"

    ncLines = ncLines + "M5\n"
    ncLines = ncLines + "G01 Z1\n"
    return ncLines


def rectangle( params, feedRate ):
    ncLines = "G00 X" + str3dec(params['x']) + " Y" + str3dec(params['y']) + "\n"
    ncLines = ncLines + "M3\n"
    ncLines = ncLines + "G0 X" + str3dec(params['x']) + " Y" + str3dec(float(params['y']) + float(params['tall'])) + " F" + str3dec(feedRate) + "\n"
    ncLines = ncLines + "G0 X" + str3dec(float(params['x']) + float(params['wide'])) + " Y" + str3dec(float(params['y']) + float(params['tall'])) + " F" + str3dec(feedRate) + "\n"
    ncLines = ncLines + "G0 X" + str3dec(float(params['x']) + float(params['wide'])) + " Y" + str3dec(params['y']) + " F" + str3dec(feedRate) + "\n"
    ncLines = ncLines + "G0 X" + str3dec(params['x']) + " Y" + str3dec(params['y']) + " F" + str3dec(feedRate) + "\n"
    ncLines = ncLines + "M5\n"
    return ncLines

def cross( params, feedRate ):
    ncLines = "n is a perfect cross\n"
    return ncLines

# map the inputs to the function blocks
cutShape = {'circle' : circle,
            'round'  : circle,
            'rectangle' : rectangle,
            'cross' : cross
}

def by_Location(cutOpp):
    y_primary_x_secondary = float( cutOpp['y'] ) * 1000 + float( cutOpp['x'] )
    return y_primary_x_secondary

def str3dec( floatNumber ):
    return str( round( float(floatNumber) ,3))

patternFile = open('input/calculator_face.json', 'r')
ncFile = open('output/calculator_face.nc', 'w')

jstr = str(patternFile.read())
cuttingOps = json.loads(jstr)
ncFileComment = str(cuttingOps)

ncFirstLine = "G17 [unit] G90 G93 G54"

if cuttingOps['config']['unit'] == 'mm' :
    ncFirstLine = str.replace(ncFirstLine, '[unit]', 'G21')
else:
    ncFirstLine = str.replace(ncFirstLine, '[unit]', 'G20')

toolRadius = float(cuttingOps['config']['tool_diameter']) * 0.5
scale = float( cuttingOps['config']['scale'] )

ncFile.write(ncFirstLine + "\n")
#ncFile.write("(" + str(ncFileComment) + ")\n") This produces a line that overloads the Grbl buffer, but it is handy for debugging in Python

# create a Python List of Dictionaries we can can sort by values
oppList = []
for oppNum, opp in cuttingOps['cuts'].iteritems():
    oppList.insert(int(oppNum), opp)

sortedOperations = sorted(oppList, key = by_Location)

# Loop through the operations
for opp in sortedOperations: # cuttingOps['cuts'].iteritems():
    opp['tempX'] = float( opp['x'] ) * scale
    opp['tempY'] = float( opp['y'] ) * scale
    if ( opp['shape'] == 'rectangle' ) : opp['wide'] = float( opp['wide'] ) * scale
    if ( opp['shape'] == 'rectangle' ) : opp['tall'] = float( opp['tall'] ) * scale
    if ( opp['shape'] == 'circle' ) : opp['radius'] = float( opp['diameter']) * 0.5 * scale
    if 'speed' in opp:
        toolSpeed = float( opp['speed'] )
    else:
        toolSpeed = float(cuttingOps['config']['default_speed'])
    #ncFile.write("G0 F" + cuttingOps['config']['default_speed'] + "\n") # set the current movement speed between cuts
    if 'array' not in opp:
        ncFile.write( cutShape[ opp['shape'] ]( opp, toolSpeed ) )
    else:
        cutArray = opp['array'] # is there an array of this shape to process ? If not do once in exception
        opp['column_spacing'] = float(opp['array']['x_spacing']) * scale
        opp['row_spacing'] = float(opp['array']['y_spacing']) * scale
        for aCol in range( 0, int(opp['array']['columns']) ):
            for aRow in range( 0, int( opp['array']['rows'] ) ):
                arrayOpp = {}
                arrayOpp['x'] = float(aCol) * opp['column_spacing'] + opp['tempX']
                arrayOpp['y'] = float(aRow) * opp['row_spacing']    + opp['tempY']
                if ( opp['shape'] == 'rectangle' ) :arrayOpp['wide'] = opp['wide']
                if ( opp['shape'] == 'rectangle' ) :arrayOpp['tall'] = opp['tall']
                if ( opp['shape'] == 'circle' ) :arrayOpp['radius'] = float( float(opp['diameter']) / 2.0 )
                ncFile.write( str(cutShape[opp['shape']]( arrayOpp, toolSpeed) ) )

# cut the border last
nextLine = 'G0 X' + str3dec(toolRadius * -1 ) + ' Y' + str3dec(toolRadius * -1 ) + " Z0 F" + cuttingOps['config']['default_speed'] + "\n"
ncFile.write(nextLine)
if 'speed' in cuttingOps['border']:
    toolSpeed = str3dec( cuttingOps['border']['speed'] )
else:
    toolSpeed = str3dec( cuttingOps['config']['default_speed'] )

ncFile.write("M3\n")
nextX = str3dec( float(toolRadius * -1) )
nextY = str3dec( float( cuttingOps['border']['y']) + toolRadius )
nextLine = "G0 X"+ nextX + " Y" + nextY + " F" + toolSpeed + "\n"
ncFile.write(nextLine)

nextX = str3dec( float(cuttingOps['border']['x']) + float(toolRadius * -1) )
nextLine = "G0 X"+ nextX + " Y" + nextY + " F" + toolSpeed + "\n"
ncFile.write(nextLine)

nextY = str3dec(toolRadius * -1 )
nextLine = "G0 X"+ nextX + " Y" + nextY + " F" + toolSpeed + "\n"
ncFile.write(nextLine)

nextX = str3dec(toolRadius * -1 )
nextLine = "G0 X"+ nextX + " Y" + nextY + " F" + toolSpeed + "\n"
ncFile.write(nextLine)

ncFile.write("M5\n")

ncFile.write('(end of script)')
ncFile.closed



