# json_to_gcode.py

A python script to convert a json file to a gcode / nc file .

Goal : Make the cnc machine cut what you want using a json array of geometry patterns, without being dependant on CAD/CAM software and independant of an proprietary file formats, and avoid the need for file conversion utilities that are prone to inaccuracies or compatibility.
 
Version v0.01 : Completed: CNC Laser ready with circles, rectangles, polygons, rectangular and circular arrays.
  
Version v0.02 : Completed : Will add some text support. Cut-Outs will become interior_cuts, laser power controlled by spindle speed for grbl shield and grbl 0.9

Version v0.02.1 : Adding default spindle speed, and adding spindle attribute to all cut routines

Version v0.02.2 : lower case letters in kajack font.

Version v0.02.3 : rotatable text

Version v0.03 : 3d Drill and text functionality for CNC Router