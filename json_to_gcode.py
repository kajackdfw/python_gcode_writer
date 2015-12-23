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

ncToolRadius = ( cuttingOps['config']['tool_diameter'] / 2 ) * -1

ncFile.write(ncFirstLine)
ncFile.write("\n")

ncFile.write("(")
ncFile.write(ncFileComment)
ncFile.write(")\n")




ncFile.write('(end of script)')
ncFile.closed
