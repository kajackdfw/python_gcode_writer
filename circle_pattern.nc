G17 G20 G90 G94 G54
({u'border': {u'y': u'3', u'x': u'3', u'shape': u'rectangle'}, u'config': {u'cut_speed': u'10', u'scale': u'0.9917', u'tool_diameter': u'0.01', u'mark_speed': u'40', u'unit': u'inches', u'mode': u'absolute'}, u'cuts': {u'0': {u'y': u'1.50', u'diameter': u'1.0', u'shape': u'circle', u'x': u'2.0'}}})
G0 X1.50415 Y1.5 Z0.1
G01 Z0. F20.0
M3
G02 X2.0 Y1.99585 I0.49585 J0.0 F20.0
X2.49585 Y1.5 I0.0 J-0.49585
X2.0 Y1.00415 I-0.49585 J0.0
X1.50415 Y1.5 I0.0 J0.49585
M5
G0 X-0.005 Y-0.005 Z0 F40
M3
G0 X-0.005 Y3.005 F10
G0 X2.995 Y3.005 F10
G0 X2.995 Y-0.005 F10
G0 X-0.005 Y-0.005 F10
M5
(end of script)