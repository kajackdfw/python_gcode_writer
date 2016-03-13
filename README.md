# json_to_gcode.py

A python script to convert a json file to a gcode / nc file .

Goal : Make the cnc machine cut what you want using a json array of geometry patterns, without being dependant on CAD/CAM software and independant of an proprietary file formats, and avoid the need for file conversion utilities that are prone to inaccuracies or compatibility.
 
Version v0.01 : Completed: CNC Laser ready with circles, rectangles, polygons, rectangular and circular arrays.
  
Version v0.02 : Started : Will add some simple text support. Border and Cut-Outs will become interior_cuts and exterior_cuts, and they will operate clockwise and counter-clockwise in anticipation of supporting CNC Router spindles in a future version with material removal support.
