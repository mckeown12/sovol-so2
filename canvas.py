##################################################
# This file is for wrapping tkinter's canvas for #
# Simulating printing with animations.           #
##################################################

from functools import partial
from oops import Polygon, Line, Point
from typing import Iterable, List
import tkinter
import numpy as np
import time
import IPython



class Canvas:

    def __init__(self, title="Window", width=1920, height=1080, ppi=110):
        self.window = tkinter.Tk()
        self.window.title(title)
        self.window.geometry(f'{width}x{height}')
        milisPerInch = 25.4
        self.pixelsPerMilimeter = ppi / milisPerInch

        self.canvas = tkinter.Canvas(self.window)
        self.canvas.configure(bg="white")
        self.canvas.pack(fill="both", expand=True)


    def performSelection(self):
        # 1.) Scroll zooms
        # 2.) click and drag pans
        # 3.) shift-click and drag adds to selection
        # 4.) ctrl-shift-click and drag removes from selection
        # 5.) Selection is approved by the "Return/Enter" key.

        shift = False
        ctrl = False
        selection = []
        self.canvas.bind("<Button-1>", self.selectionHandler)
        self.canvas.bind("<Key-Down>", self.selectionHandler)
        self.canvas.bind("<Key-Up>", self.selectionHandler)
        self.canvas.bind("<MouseWheel>", self.selectionHandler)
        self.canvas.bind("<Return>", self.selectionHandler)

        return [[0,0,100,100]] # as an example, just one rectangle from (0,0) to (100,100)

    def selectionHandler(self, event):
        print("Selection Handler")
        

    def drawGcode(self, gcode):
        pass


    def simulateLaser(self, line: Line, speed: int, height: int, intensity: int):

        if isinstance(line, Iterable):
            assert len({len(line), len(speed), len(height), len(intensity)}) == 1, "all arguments must have the same length!"

            for l,s,h,i in zip(line,speed,height,intensity):
                self.simulateLaser(l,s,h,i)
        
        else:
            s = self.pixelsPerMilimeter
            canvasLine = self.canvas.create_line(line.p1.x*s, line.p1.y*s, line.p2.x*s, line.p2.y*s)
            RESOLUTION = 10
            sleepPerMilimiter = 1 / speed
            milimitersPerIteration = line.length() / RESOLUTION
            sleepPerIteration = sleepPerMilimiter * milimitersPerIteration


            for offset in np.linspace(0, line.length(), RESOLUTION):
                p2 = line.pointAtOffset(offset)
                self.canvas.coords(canvasLine, [line.p1.x*s, line.p1.y*s, p2.x*s, p2.y*s])
                # color = f"rgb({int((intensity/1000)*255)}, 0, 0)"
                color = "black"

                self.canvas.itemconfig(canvasLine, fill=color)
                self.window.update()
                time.sleep(sleepPerIteration)
            


