import json

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
    ncLines = "G0 X" + str(params['x']) + " Y" + str( float(params['y']) + radius ) + " F40\n"
    ncLines = ncLines + "M3\n"
    # G02 X0. Y0.5 I0.5 J0. F2.5
    # X0.5 Y0. I0. J-0.5
    # X0. Y-0.5 I-0.5 J0.
    # X-0.5 Y0. I0. J0.5
    ncLines = ncLines + "G02 X" + str(float(params['x']) + radius ) + " Y" + str( params['y'] ) + " I" + str(radius) + " J0. F2" + str(feedRate)
    ncLines = ncLines + "circle"
    ncLines = ncLines + "M5\n"
    return ncLines

def rectangle( params, feedRate ):
    ncLines = "G0 X" + str(params['x']) + " Y" + str(params['y']) + " F40\n"
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


patternFile = open('calculator_face.json', 'r')
ncFile = open('calculator_face.nc', 'w')

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

ncFile.write(ncFirstLine)
ncFile.write("\n")

ncFile.write("(")
ncFile.write(ncFileComment)
ncFile.write(")\n")

nextLine = 'G0 X' + str(toolRadius * -1 ) + ' Y' + str(toolRadius * -1 ) + " Z0 F40\n"
ncFile.write(nextLine)


# Loop through the CUTS
for oppNum, opp in cuttingOps['cuts'].iteritems():
    adjusted = []
    opp['tempX'] = float( opp['x'] ) * scale
    opp['tempY'] = float( opp['y'] ) * scale
    if ( opp['shape'] == 'rectangle' ) : opp['wide'] = float( opp['wide'] ) * scale
    if ( opp['shape'] == 'rectangle' ) : opp['tall'] = float( opp['tall'] ) * scale
    if ( opp['shape'] == 'circle' ) : opp['radius'] = float( opp['diameter']) * 0.5 * scale
    try:
        cutArray = opp['array'] # is there an array of this shape to process ? If not do once in exception
        opp['column_spacing'] = float(opp['array']['x_spacing']) * scale
        opp['row_spacing'] = float(opp['array']['y_spacing']) * scale
        print "spacings cleaned up for opp # = " + str(oppNum)
        print "start drawing " + str( opp['array']['columns'] ) + " columns"
        for aCol in range( 0, int(opp['array']['columns']) ):
            print "   aCol = " + str(aCol)
            print "   start drawing " + str( opp['array']['rows'] ) + " rows , spaced at " + str( opp['row_spacing'] )
            for aRow in range( 0, int( opp['array']['rows'] ) ):
                arrayOpp = {}
                arrayOpp['x'] = float(aCol) * opp['column_spacing'] + opp['tempX']
                arrayOpp['y'] = float(aRow) * opp['row_spacing']    + opp['tempY']
                arrayOpp['wide'] = opp['wide']
                arrayOpp['tall'] = opp['tall']
                ncFile.write( str(cutShape[opp['shape']]( arrayOpp, cuttingOps['config']['cut_speed'])) )
    except KeyError:
        # Array key is not present
        print "exception: missing array element for opp # = " + str(oppNum)
        ncFile.write( cutShape[ opp['shape'] ]( opp, cuttingOps['config']['cut_speed'] ) )

# cut the border
ncFile.write("M3\n")
nextX = str( float(toolRadius * -1) )
nextY = str( float( cuttingOps['border']['y']) + toolRadius )
nextLine = "G0 X"+ nextX + " Y" + nextY + " F" + str( cuttingOps['config']['cut_speed'] ) + "\n"
ncFile.write(nextLine)

nextX = str( float(cuttingOps['border']['x']) + float(toolRadius * -1) )
nextLine = "G0 X"+ nextX + " Y" + nextY + " F" + str( cuttingOps['config']['cut_speed'] ) + "\n"
ncFile.write(nextLine)

nextY = str(toolRadius * -1 )
nextLine = "G0 X"+ nextX + " Y" + nextY + " F" + str( cuttingOps['config']['cut_speed'] ) + "\n"
ncFile.write(nextLine)

nextX = str(toolRadius * -1 )
nextLine = "G0 X"+ nextX + " Y" + nextY + " F" + str( cuttingOps['config']['cut_speed'] ) + "\n"
ncFile.write(nextLine)

ncFile.write("M5\n")

ncFile.write('(end of script)')
ncFile.closed



