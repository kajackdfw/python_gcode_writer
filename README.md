# json_to_gcode.py


A python script to convert a json file to a gcode / nc file .

**Goal** : Make the cnc machine cut what you want using a json array of geometry patterns, without being dependant on CAD/CAM software and independant of an proprietary file formats, and avoid the need for file conversion utilities that are prone to inaccuracies or compatibility.
 
**Sample Files** : There are some sample input files in the patterns/ folder. Inside patterns/ there are two sub folders. router/ and laser/ . Laser patterns are just 2d while the router patterns are 3D.
  
**Usage** : On the command line ...
>cd python_gcode_writer
>python json_to_gcode.py patterns/router/vacuum_table_holes.json nc/my_test.nc

**Preview NC File** : There is an online tool to preview the new file before sending it to your cnc machine.

visit : http://http://chilipeppr.com/grbl  and drag and drop your new NC file into this page.

**Version v0.03.03 : development for this has ended, after being forked to https://github.com/kajackdfw/python_cattern_engine** 

Version v0.03.02 : improved drill functionality

Version v0.03.01 : fixed radial copies of lines

Version v0.03 : 3d Drill and text functionality for CNC Router

Version v0.02.3 : rotatable text

Version v0.02.2 : lower case letters in kajack font.

Version v0.02.1 : Adding default spindle speed, and adding spindle attribute to all cut routines

Version v0.02 : Completed : Will add some text support. Cut-Outs will become interior_cuts, laser power controlled by spindle speed for grbl shield and grbl 0.9

Version v0.01 : Completed: CNC Laser ready with circles, rectangles, polygons, rectangular and circular arrays.