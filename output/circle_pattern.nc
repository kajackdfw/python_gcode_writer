G17 G21 G90 G94 G54
G00 X10.0 Y15.0 
M3
G01 X10.0 Y35.544 F200.0
G02 X10.0 Y40.544 I5.0 J0 F500
G01 X35.544 Y40.544 F200.0
G02 X40.544 Y40.544 I5.0 J-5.0 F500
G01 X40.544 Y15.0 F200.0
G02 X40.544 Y10.0 I5.0 J5.0 F500
G01 X15.0 Y10.0 F200.0
G02 X10.0 Y10.0 I0 J5.0 F500
M5
G0 X-0.01 Y-0.01 Z0 F200
M3
G01 X-0.01 Y50.81 F200.0
G01 X50.79 Y50.81 
G01 X50.79 Y-0.01 
G01 X-0.01 Y-0.01 
M5
(end of script)