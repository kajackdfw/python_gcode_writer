import json

# Config Settings
# G17 XY Plane
# G18 XZ Plane
# G19 YZ Plane
# G20 Inch mode
# G21 mm mode
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

patternFile = open('calculator_face.json', 'r')
ncFile = open('calculator_face.nc', 'w')

jstr = str(patternFile.read())
cuttingOps = json.loads(jstr)
ncFileComment = str(cuttingOps)

ncFirstLine = "G17 [unit] [mode] G94"

if cuttingOps['config']['unit'] == 'mm' :
    ncFirstLine = str.replace(ncFirstLine, '[unit]', 'G21')
else:
    ncFirstLine = str.replace(ncFirstLine, '[unit]', 'G20')

if cuttingOps['config']['mode'] == 'absolute' :
    ncFirstLine = str.replace(ncFirstLine, '[mode]', 'G90')
else:
    ncFirstLine = str.replace(ncFirstLine, '[mode]', 'G91')

ncToolRadius = float(cuttingOps['config']['tool_diameter']) * 0.5

ncFile.write(ncFirstLine)
ncFile.write("\n")

ncFile.write("(")
ncFile.write(ncFileComment)
ncFile.write(")\n")

nextLine = 'G0 X' + str(ncToolRadius * -1 ) + ' Y' + str(ncToolRadius * -1 ) + " Z0 F40\n"
ncFile.write(nextLine)


# loop through the cuts
for opp in cuttingOps:
    try:
        cutArray = opp['array']
    except KeyError:
        # Key is not present
        pass

# http://stackoverflow.com/questions/11479816/what-is-the-python-equivalent-for-a-case-switch-statement

# cut the border
ncFile.write("M3\n")
nextX = str( float(ncToolRadius * -1) )
nextY = str( float( cuttingOps['border']['y']) + ncToolRadius )
nextLine = "G0 X"+ nextX + " Y" + nextY + " F" + str( cuttingOps['config']['cut_speed'] ) + "\n"
ncFile.write(nextLine)

nextX = str( float(cuttingOps['border']['x']) + float(ncToolRadius * -1) )
nextLine = "G0 X"+ nextX + " Y" + nextY + " F" + str( cuttingOps['config']['cut_speed'] ) + "\n"
ncFile.write(nextLine)

nextY = str(ncToolRadius * -1 )
nextLine = "G0 X"+ nextX + " Y" + nextY + " F" + str( cuttingOps['config']['cut_speed'] ) + "\n"
ncFile.write(nextLine)

nextX = str(ncToolRadius * -1 )
nextLine = "G0 X"+ nextX + " Y" + nextY + " F" + str( cuttingOps['config']['cut_speed'] ) + "\n"
ncFile.write(nextLine)

ncFile.write("M5\n")

ncFile.write('(end of script)')
ncFile.closed


# define the function blocks
def circle( oppInfo ):
    print "You typed zero.\n"

def rectangle( oppInfo ):
    print "n is a perfect square\n"

# map the inputs to the function blocks
options = {'circle' : circle,
           'rectangle' : rectangle
}
