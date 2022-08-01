from collections import namedtuple
from typing import Iterable, List, Tuple
import math
import numpy as np


class Point:
    def __init__(self, x,y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)
    
    def __mul__(self, other):
        return Point(self.x * other, self.y * other)
    
    def __rmul__(self, other):
        return Point(self.x * other, self.y * other)
    
    def length(self):
        return math.sqrt(self.x**2 + self.y**2)
    
    def normalize(self, mutate=False):
        l = self.length()
        if mutate:
            self.x /= l
            self.y /= l
        else:
            return Point(self.x / l, self.y / l)

ORIGIN = Point(0,0)

class Line:

    def __init__(self, p1: Point, p2: Point):
        self.p1 = p1
        self.p2 = p2

    def translate(self, v: Point, mutate=False):
        if mutate:
            self.p1 = self.p1 + v
            self.p2 = self.p2 + v
        else:
            return Line(self.p1 + v,self.p2 + v)
    
    def flip(self, mutate=False):
        if mutate:
            self.p1, self.p2 = self.p2, self.p1
        else:
            return Line(self.p2, self.p1)
    
    def gCode(self, speed, height, laserIntensity=1000):
        s1 = f"G0 X{self.p1.x} Y{self.p1.y} Z{height} F{speed} S{0}"
        s2 = f"G1 X{self.p2.x} Y{self.p2.y} Z{height} F{speed} S{laserIntensity}"
        return s1 + "\n" + s2 + "\n"
    
    def pointAtOffset(self, offset):
        unitDiff = (self.p2 - self.p1).normalize()
        return self.p1 + (unitDiff * offset)

    def addTabs(self, offsets, lengths, thickness, innie=False):
        points = [self.p1]

        # Find a perpendicular unit vector (There's probably a better way)
        diff = self.p2 - self.p1
        b = 10
        a = -b*diff.y / diff.x
        unitPerp = Point(a,b).normalize()
        if innie:
            unitPerp = unitPerp*-1
        unit = (self.p2 - self.p1).normalize()

        for offset, length in zip(offsets, lengths):
            tabVert1 = self.pointAtOffset(offset)
            tabVert2 = tabVert1 + (unitPerp * thickness)
            tabVert3 = tabVert2 + (unit * length)
            tabVert4 = tabVert3 - (unitPerp * thickness)
            points.extend([tabVert1, tabVert2, tabVert3, tabVert4])
        points.append(self.p2)

        lines = [Line(a,b) for a,b in zip(points, points[1:])]
        return lines

    def length(self):
        diff = self.p2 - self.p1
        return diff.length()


class Polygon:

    def __init__(self, lines: List[Line]):
        self.lines = lines
    
    def translate(self, v: Point, mutate=False):
        if mutate:
            for l in self.lines:
                l.translate(v, mutate=True)
        else:
            return Polygon([line.translate(v, mutate=False) for line in self.lines])

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


class Box:
    """
    This class is for making 3D Objects
    composed of interlocking faces.
    Each face is a Polygon and these Polygons can be edited
    to interlock using the interlock method of this class.
    """

    def __init__(self, faces):
        self.faces = faces
    
    @staticmethod
    def interlock(line1, line2, tabWidths=15, tabCount=2, thickness=5, padding=20):
        """This method returns (lines1, lines2) 
        where lines1 is a list of lines meant to replace line1
        and lines2 is a list of lines meant to replace line2.
        This method is responsible for placing and spacing tabs.
        The actual generation of the lines is done in "addTab"
        """
        assert abs(line1.length() - line2.length()) < 1, "Interlocking lines must be the same length!"

        if isinstance(tabWidths, Iterable):
            assert sum(tabWidths) < line1.length()-2*padding, "Tab widths cannot together exceed the length of the interlocking lines (minus 2*padding)!"
            raise NotImplementedError
        else:
            assert tabWidths*tabCount < line1.length()-2*padding, "The space allocated for tabs cannot exceed the length of the interlocking lines (minus 2*padding)!"
            line2 = line2.flip() # <-- this is weird and has to be thought of more.
        
            # Evenly space tabs.
            tabCenters = np.linspace(padding, line1.length() - padding, tabCount)
            offsets = [c-(tabWidths/2) for c in tabCenters]
            tabWidths = [tabWidths for _ in offsets]

        lines1 = line1.addTabs(offsets, tabWidths, thickness)
        lines2 = line2.addTabs(offsets, tabWidths, thickness, innie=True)
        return lines1, lines2







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