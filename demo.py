
from oops import Rectangle, Point, Line, Polygon, Box
from canvas import Canvas
import time

canvas = Canvas("Demo Time!")

r1 = Rectangle(Point(100,100), Point(200,400))
r2 = Rectangle(Point(500,500), Point(600,700))

r1Lines, r2Lines = Box.interlock(r1.lines[0], r2.lines[0])

r1Lines += r1.lines[1:]
r2Lines += r2.lines[1:]

lines = r1Lines + r2Lines
speeds = [500 for _ in lines]
heights = [1 for _ in lines]
intensities = [1000 for _ in lines]

canvas.simulateLaser(lines, speeds, heights, intensities)

time.sleep(5)

