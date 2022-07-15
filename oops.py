from collections import namedtuple
from typing import Iterable, List
import math

Point = namedtuple("Point", ["x", "y"])

class Line:

    def __init__(self, p1: Point, p2: Point):
        self.p1 = p1
        self.p2 = p2

    def translate(self, v: Point):
        self.p1.x += v.x
        self.p1.y += v.y
        self.p2.x += v.x
        self.p2.y += v.y

    def gCode(self, speed, height, laserIntensity=1000):
        s1 = f"G0 X{self.p1.x} Y{self.p1.y} Z{height} F{speed} S{0}"
        s2 = f"G1 X{self.p2.x} Y{self.p2.y} Z{height} F{speed} S{laserIntensity}"
        return s1 + "\n" + s2 + "\n"

class Polygon:

    def __init__(self, lines: List[Line]):
        self.lines = lines
    
    def translate(self, v: Point):
        for l in self.lines:
            l.translate(v)

    @staticmethod
    def regularPolygon(n: int, radius: float, center: Point):
        lines = []
        for i in range(n):
            angle = 2 * i * math.pi / n
            p1 = Point(center.x + radius * math.cos(angle), center.y + radius * math.sin(angle))
            p2 = Point(center.x + radius * math.cos(angle + math.pi / n), center.y + radius * math.sin(angle + math.pi / n))
            lines.append(Line(p1, p2))
        return Polygon(lines)


    def gCode(self, speed, height, laserIntensity=1000):
        strings = []
        for i,l in enumerate(self.lines):
            s = speed
            if isinstance(speed, Iterable):
                s = speed[i]

            h = height
            if isinstance(height, Iterable):
                h = height[i]

            intensity = laserIntensity
            if isinstance(laserIntensity, Iterable):
                intensity = laserIntensity[i]

            strings.append(l.gCode(s,h,intensity))
        return "\n".join(strings)

class Rectangle(Polygon):
    
    def __init__(self, p1: Point, p2: Point):
        lines = [Line(p1, Point(p2.x, p1.y)), Line(Point(p2.x, p1.y), p2), Line(p2, Point(p1.x, p2.y)), Line(Point(p1.x, p2.y), p1)]
        super().__init__(lines)





class MandleBrot:

    def __init__(self, xres, yres, xmin, xmax, ymin, ymax):
        self.table = []
        self.xres = xres
        self.yres = yres
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        for i in range(xres):
            col = []
            for j in range(yres):
                real = xmin + i * (xmax - xmin) / xres
                imag =  ymin + j * (ymax - ymin) / yres
                col.append(MandleBrot.in_set(real, imag))
            self.table.append(col)
        self.table = list(map(list, zip(*self.table)))

    @staticmethod
    def in_set(real, imag, maxIterations=10, limit=1000):
        z = 0
        c = (real + imag * 1j)
        for i in range(maxIterations):
            z = z**2 + c
            if abs(z) > limit:
                return False
        return True

    def gCode(self, scale=1):
        s = ""
        for i, row in enumerate(self.table):
            s += f"G1 X{self.xmin + i * (self.xmax - self.xmin) / self.xres} Y{self.ymin} S0\n"
            for j,col in enumerate(row):
                if col:
                    s += f"G1 X{self.xmin + i * (self.xmax - self.xmin) / self.xres} Y{self.ymin + j * (self.ymax - self.ymin) / self.yres} S1000\n"
                else:
                    s += f"G1 X{self.xmin + i * (self.xmax - self.xmin) / self.xres} Y{self.ymin + j * (self.ymax - self.ymin) / self.yres} S0\n"
            s += "\n"
        return s