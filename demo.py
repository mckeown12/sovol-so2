
from oops import Rectangle, Point, Line, Polygon, Box
from canvas import Canvas
import time

canvas = Canvas("Demo Time!")

r1 = Rectangle(Point(10,10), Point(60,60))
r2 = Rectangle(Point(10,60), Point(60,120))
r2.translate(Point(0,20), mutate=True)

def interlock(lines1, lines2, i,j, *args, flipI=False, flipJ=False, **kwargs):
    l1 = lines1[i].flip() if flipI else lines1[i]
    l2 = lines2[j].flip() if flipJ else lines2[j]
    repl1, repl2 = Box.interlock(l1, l2, *args, **kwargs)
    
    out1, out2 = [],[]
    for idx, l in enumerate(lines1):
        if idx == i:
            out1.extend(repl1)
        else:
            out1.append(l)
    
    for idx, l in enumerate(lines2):
        if idx == j:
            out2.extend(repl2)
        else:
            out2.append(l)

    return out1, out2

r1Lines, r2Lines = interlock(r1.lines, r2.lines, 2, 0, tabWidths=5, tabCount=3, thickness=2, padding=10)


lines = r1Lines + r2Lines
speeds = [500 for _ in lines]
heights = [1 for _ in lines]
intensities = [1000 for _ in lines]

canvas.simulateLaser(lines, speeds, heights, intensities)
myPoly = Polygon(lines)
gcode = myPoly.gCode(speeds, heights, intensities)
with open("demo.gcode", "w") as f:
    f.write(gcode)
time.sleep(10)

