import json

patternFile = open('calculator_face.json', 'r')
ncFile = open('calculator_face.nc', 'w')

jstr = patternFile.read()

cuttingOps = json.loads(jstr)

ncFile.write(cuttingOps)

ncFile.closed
