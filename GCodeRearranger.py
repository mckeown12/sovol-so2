import argparse
from canvas import Canvas
import re

import IPython


def inRect(x1,y1, x2,y2, x3,y3):
    """Boolean to tell if (x1,y1) is within the rectangle defined by (x2,y2) and (x3,y3)"""
    xmin, xmax = sorted([x2,x3])
    ymin, ymax = sorted([y2,y3])
    return (xmin <= x1 and x1 <= xmax) and (ymin <= y1 and y1 <= ymax)


def SelectPrint(gcode, bedWidth, bedHeight):

    # Setup canvas and draw GCode
    c = Canvas("Select region to print")
    c.drawGcode(gcode)

    # Evoke input from user to select lines
    selection = c.performSelection()

    #TODO: Edit gcode accordingly:
    keep = []
    for line in gcode.split("\n"):
        match = re.search(r"\s*(G0[01])\s*X([0-9\.]+)\s*Y([0-9\.]+)", line)
        
        if match:
            mode, x, y = match[1],float(match[2]), float(match[3])
            if any([inRect(x,y, x1,y1,x2,y2) for x1,y1,x2,y2 in selection]):
                keep.append((mode,x,y))
        else:
            keep.append(line)
        
    xmin = min(t[1] for t in keep if isinstance(t,tuple))
    ymin = min(t[2] for t in keep if isinstance(t,tuple))
    for i,line in enumerate(keep):
        if isinstance(line, tuple):
            mode, x,y = line
            keep[i] = f"{mode} X{x - xmin} Y{y - ymin}"

    return "\n".join(keep)




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="exampleBadGcode.gcodeFIXED")
    parser.add_argument("--output", default="exampleBadGcode.gcodeFIXED_Selected")
    args = parser.parse_args()

    with open(args.input) as f:
        gcode = f.read()
    
    selected = SelectPrint(gcode, 280, 180)

    with open(args.output, "w") as f:
        f.write(selected)
