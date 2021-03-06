##################################################
# This file is for wrapping tkinter's canvas for #
# Simulating printing with animations.           #
##################################################

from oops import Polygon, Line, Point
from typing import Iterable, List
import tkinter
import numpy as np
import time
import IPython



class Canvas:

    def __init__(self, title="Window", width=1920, height=1080):
        self.window = tkinter.Tk()
        self.window.title(title)
        self.window.geometry(f'{width}x{height}')

        self.canvas = tkinter.Canvas(self.window)
        self.canvas.configure(bg="white")
        self.canvas.pack(fill="both", expand=True)


    def simulateLaser(self, line: Line, speed: int, height: int, intensity: int):

        if isinstance(line, Iterable):
            assert len({len(line), len(speed), len(height), len(intensity)}) == 1, "all arguments must have the same length!"

            for l,s,h,i in zip(line,speed,height,intensity):
                self.simulateLaser(l,s,h,i)
        
        else:
            canvasLine = self.canvas.create_line(line.p1.x, line.p1.y, line.p2.x, line.p2.y)
            RESOLUTION = 10
            sleepPerMilimiter = 1 / speed
            milimitersPerIteration = line.length() / RESOLUTION
            sleepPerIteration = sleepPerMilimiter * milimitersPerIteration


            for offset in np.linspace(0, line.length(), RESOLUTION):
                p2 = line.pointAtOffset(offset)
                self.canvas.coords(canvasLine, [line.p1.x, line.p1.y, p2.x, p2.y])
                # color = f"rgb({int((intensity/1000)*255)}, 0, 0)"
                color = "black"

                self.canvas.itemconfig(canvasLine, fill=color)
                self.window.update()
                time.sleep(sleepPerIteration)
            


