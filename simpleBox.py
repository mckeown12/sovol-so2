
from oops import Rectangle, Point, Line, Polygon, Box
from canvas import Canvas
import time
import itertools

canvas = Canvas("Demo Time!")


def interlock(lines1, lines2, i,j, *args, flipI=False, flipJ=False, **kwargs):
    l1 = lines1[i].flip() if flipI else lines1[i]
    l2 = lines2[j].flip() if flipJ else lines2[j]
    repl1, repl2 = Box.interlock(l1, l2, *args, **kwargs)
    
    out1 = [repl1 if idx == i else l for idx, l in enumerate(lines1)]
    out2 = [repl2 if idx == j else l for idx, l in enumerate(lines2)]

    return out1, out2


scale = 4
pad = 13

front = Rectangle(Point(0,0), Point(10,10))
back = front.translate(Point(pad, 0))

left = Rectangle(Point(0,0), Point(10,10)).translate(Point(0, pad))
right = left.translate(Point(pad, 0))

top = Rectangle(Point(0,0), Point(10,10)).translate(Point(0, 2*pad))
bottom = top.translate(Point(pad, 0))


front,back,left,right,top,bottom = [r.scale(scale) for r in [front,back,left,right,top,bottom]]
front,back,left,right,top,bottom = [r.translate(Point(5,5)) for r in [front,back,left,right,top,bottom]]


front.lines, left.lines = interlock(front.lines, left.lines, 3, 1, tabWidths=3, tabCount=2, thickness=2, padding=10)
front.lines, right.lines = interlock(front.lines, right.lines, 1, 3, tabWidths=3, tabCount=2, thickness=2, padding=10)
front.lines, top.lines = interlock(front.lines, top.lines, 0, 0, tabWidths=3, tabCount=2, thickness=2, padding=10)
front.lines, bottom.lines = interlock(front.lines, bottom.lines, 2, 0, tabWidths=3, tabCount=2, thickness=2, padding=10)

top.lines, right.lines = interlock(top.lines, right.lines, 3, 0, tabWidths=3, tabCount=2, thickness=2, padding=10)
top.lines, left.lines = interlock(top.lines, left.lines, 1, 0, tabWidths=3, tabCount=2, thickness=2, padding=10)
top.lines, back.lines = interlock(top.lines, back.lines, 2, 0, tabWidths=3, tabCount=2, thickness=2, padding=10)

back.lines, left.lines = interlock(back.lines, left.lines, 1, 3, tabWidths=3, tabCount=2, thickness=2, padding=10)
back.lines, right.lines = interlock(back.lines, right.lines, 3, 1, tabWidths=3, tabCount=2, thickness=2, padding=10)
back.lines, bottom.lines = interlock(back.lines, bottom.lines, 2, 2, tabWidths=3, tabCount=2, thickness=2, padding=10)

bottom.lines, right.lines = interlock(bottom.lines, right.lines, 1, 2, tabWidths=3, tabCount=2, thickness=2, padding=10)
bottom.lines, left.lines = interlock(bottom.lines, left.lines, 3, 2, tabWidths=3, tabCount=2, thickness=2, padding=10)

# Flattening lists...
lines = []
for line in front.lines + back.lines + left.lines + right.lines + top.lines + bottom.lines:
    if isinstance(line, Line):
        lines.append(line)
    else:
        lines.extend(line)

simSpeeds = [1000 for _ in lines]
speeds = [250 for _ in lines]

heights = [3 for _ in lines]
intensities = [1000 for _ in lines]

canvas.simulateLaser(lines, simSpeeds, heights, intensities)
myPoly = Polygon(lines)
gcode = myPoly.gCode(speeds, heights, intensities)
with open("simpleBox.gcode", "w") as f:
    f.write(gcode)
time.sleep(60)

