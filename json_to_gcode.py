import json

# TODOS : feedrate is behaving differently for rectangles and circles

# Config Settings
# G17 XY Plane
# G18 XZ Plane
# G19 YZ Plane
# G20 Inch mode
# G21 mm mode
# G54 circle mode
# G90 absolute coordinates
# G91 relative mode
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

    ncLines = "G0 X" + str(leftPt) + " Y" + str(y) + " Z0.1\n"
    ncLines = ncLines + "G01 Z0.0\n"
    ncLines = ncLines + "M3\n"
    ncLines = ncLines + "G02 X" + str(x)       + " Y" + str(topPt)      + " I" + str(radius)    + " J0.0 F" + str(feedRate) + "\n"
    ncLines = ncLines +     "X" + str(rightPt) + " Y" + str(y)          + " I0.0 J"             + str( negRadius ) + "\n"
    ncLines = ncLines +     "X" + str(x)       + " Y" + str( bottomPt ) + " I" + str(negRadius) + " J0.0\n"
    ncLines = ncLines +     "X" + str(leftPt)  + " Y" + str(y)          + " I0.0 J"             + str( radius ) + "\n"
    ncLines = ncLines + "M5\n"

    return ncLines

def rectangle( params, feedRate ):
    ncLines = "G0 X" + str(params['x']) + " Y" + str(params['y']) + "\n"
    ncLines = ncLines + "M3\n"
    ncLines = ncLines + "G0 X" + str(float(params['x']) + float(params['wide'])) + " Y" + str(params['y']) + " F" + str(feedRate) + "\n"
    ncLines = ncLines + "G0 X" + str(float(params['x']) + float(params['wide'])) + " Y" + str(float(params['y']) + float(params['tall'])) + " F" + str(feedRate) + "\n"
    ncLines = ncLines + "G0 X" + str(params['x']) + " Y" + str(float(params['y']) + float(params['tall'])) + " F" + str(feedRate) + "\n"
    ncLines = ncLines + "G0 X" + str(params['x']) + " Y" + str(params['y']) + " F" + str(feedRate) + "\n"
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


patternFile = open('input/test_pattern.json', 'r')
ncFile = open('output/test_pattern.nc', 'w')

jstr = str(patternFile.read())
cuttingOps = json.loads(jstr)
ncFileComment = str(cuttingOps)

ncFirstLine = "G17 [unit] [mode] G94 G54"

if cuttingOps['config']['unit'] == 'mm' :
    ncFirstLine = str.replace(ncFirstLine, '[unit]', 'G21')
else:
    ncFirstLine = str.replace(ncFirstLine, '[unit]', 'G20')

if cuttingOps['config']['mode'] == 'absolute' :
    ncFirstLine = str.replace(ncFirstLine, '[mode]', 'G90')
else:
    ncFirstLine = str.replace(ncFirstLine, '[mode]', 'G91')

toolRadius = float(cuttingOps['config']['tool_diameter']) * 0.5
scale = float( cuttingOps['config']['scale'] )

ncFile.write(ncFirstLine + "\n")
#ncFile.write("(" + str(ncFileComment) + ")\n") This produces a line that overloads the Grbl buffer, but it is handy for debugging in Python

# sort the cuts ascending from bottom to top by 'y' value
# sorted( cuttingOps['cuts'].  ??? ['y'] ??? )

# Loop through the CUTS
for oppNum, opp in cuttingOps['cuts'].iteritems():
    opp['tempX'] = float( opp['x'] ) * scale
    opp['tempY'] = float( opp['y'] ) * scale
    if ( opp['shape'] == 'rectangle' ) : opp['wide'] = float( opp['wide'] ) * scale
    if ( opp['shape'] == 'rectangle' ) : opp['tall'] = float( opp['tall'] ) * scale
    if ( opp['shape'] == 'circle' ) : opp['radius'] = float( opp['diameter']) * 0.5 * scale
    #toolSpeed = float(cuttingOps['config']['default_speed'])
    if 'speed' in opp:
        toolSpeed = float( opp['speed'] )
    else:
        toolSpeed = float(cuttingOps['config']['default_speed'])
    ncFile.write("G0 F" + cuttingOps['config']['default_speed'] + "\n") # set the current movement speed between cuts
    if 'array' not in opp:
        ncFile.write( cutShape[ opp['shape'] ]( opp, toolSpeed ) )
    else:
        cutArray = opp['array'] # is there an array of this shape to process ? If not do once in exception
        opp['column_spacing'] = float(opp['array']['x_spacing']) * scale
        opp['row_spacing'] = float(opp['array']['y_spacing']) * scale
        print "spacings cleaned up for opp # = " + str(oppNum)
        print "start drawing " + str( opp['array']['columns'] ) + " columns"
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
nextLine = 'G0 X' + str(toolRadius * -1 ) + ' Y' + str(toolRadius * -1 ) + " Z0 " + cuttingOps['config']['default_speed'] + "\n"
ncFile.write(nextLine)
if 'speed' in cuttingOps['border']:
    toolSpeed = str( cuttingOps['border']['speed'] )
else:
    toolSpeed = str( cuttingOps['config']['default_speed'] )

ncFile.write("M3\n")
nextX = str( float(toolRadius * -1) )
nextY = str( float( cuttingOps['border']['y']) + toolRadius )
nextLine = "G0 X"+ nextX + " Y" + nextY + " F" + toolSpeed + "\n"
ncFile.write(nextLine)

nextX = str( float(cuttingOps['border']['x']) + float(toolRadius * -1) )
nextLine = "G0 X"+ nextX + " Y" + nextY + " F" + toolSpeed + "\n"
ncFile.write(nextLine)

nextY = str(toolRadius * -1 )
nextLine = "G0 X"+ nextX + " Y" + nextY + " F" + toolSpeed + "\n"
ncFile.write(nextLine)

nextX = str(toolRadius * -1 )
nextLine = "G0 X"+ nextX + " Y" + nextY + " F" + toolSpeed + "\n"
ncFile.write(nextLine)

ncFile.write("M5\n")

ncFile.write('(end of script)')
ncFile.closed



