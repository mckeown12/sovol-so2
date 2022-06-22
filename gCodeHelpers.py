import sys
gcode = '''G0 X0 Y0 F1000
M4 S1000
'''

def burnTo(x,y, mmPerMinute=3000, strength=50, gcode=gcode):
    gcode = gcode + f'''
G1 X{x}Y{y}'''#F{mmPerMinute}S{strength}'''
    return gcode

def burnFromTo(x0,y0, x1,y1, gcode=gcode, **kwargs):
    gcode = moveTo(x0,y0, gcode=gcode, **kwargs)
    gcode = burnTo(x1,y1, gcode=gcode, **kwargs)
    return gcode

def moveTo(x,y, gcode=gcode):
    gcode = gcode + f'''
G0X{x}Y{y}'''
    return gcode

def makeGrid(x0=0,y0=0, x1=210, y1=280, spacing=10, gcode=gcode, **kwargs):
    for i in range(int((y1-y0)/spacing)+1):
        gcode = burnFromTo(x0, y0+i*spacing, x1, y0+i*spacing, gcode)
    for i in range(int((x1-x0)/spacing)+1):
        gcode = burnFromTo(x0+i*spacing, y0, x0+i*spacing, y1, gcode)

    return gcode

gcode = makeGrid()
#finally
gcode = gcode + '''
G0 x0 Y0 S0
M5
'''