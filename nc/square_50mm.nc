G17 G21 G90 G94 G54
(circle 8.5 radius) 
G00 X47.0 Y55.5 
M3
G02 X55.5 Y64.0 I8.5 J0. F500.0
X64.0 Y55.5 I0.0 J-8.5
X55.5 Y47.0 I-8.5 J0.0
X47.0 Y55.5 I0.0 J8.5
M5
(rectangle)
G00 X0.5 Y6.0 
M3
G01 X0.5 Y106.0 F10.0
(start corner radius at 6.0, 106.0)
G01 X0.919 Y108.105
G01 X2.111 Y109.889
G01 X3.895 Y111.081
G01 X6.0 Y111.5
(end corner)
G01 X106.0 Y111.5 F10.0
(start corner radius at 106.0, 106.0)
G01 X108.105 Y111.081
G01 X109.889 Y109.889
G01 X111.081 Y108.105
G01 X111.5 Y106.0
(end corner)
G01 X111.5 Y6.0 F10.0
(start corner radius at 106.0, 6.0)
G01 X111.081 Y3.895
G01 X109.889 Y2.111
G01 X108.105 Y0.919
G01 X106.0 Y0.5
(end corner)
G01 X6.0 Y0.5 F10.0
(start corner radius at 6.0, 6.0)
G01 X3.895 Y0.919
G01 X2.111 Y2.111
G01 X0.919 Y3.895
G01 X0.5 Y6.0
(end corner)
M5
(end of script)