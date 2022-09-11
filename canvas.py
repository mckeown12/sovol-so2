##################################################
# This file is for wrapping tkinter's canvas for #
# Simulating printing with animations.           #
##################################################

from functools import partial
from random import random
from oops import Polygon, Line, Point
from typing import Iterable, List
import tkinter
import numpy as np
import time
import re
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

        self.shift = False
        self.alt = False
        self.clickStart = None
        self.selectRect = None
        self.selection = []


    def printToCanvas(self, x,y):
        newX = x * self.pixelsPerMilimeter * self.scale + self.offset[0]
        newY = y * self.pixelsPerMilimeter * self.scale + self.offset[1]
        return newX, newY

    def canvasToPrint(self, x,y):
        newX = (x - self.offset[0]) / (self.pixelsPerMilimeter * self.scale)
        newY = (y - self.offset[1]) / (self.pixelsPerMilimeter * self.scale)
        return newX, newY


    def performSelection(self, gcode):
        # 1.) Scroll zooms
        # 2.) click and drag pans
        # 3.) shift-click and drag adds to selection
        # 4.) ctrl-shift-click and drag removes from selection
        # 5.) Selection is approved by the "Return/Enter" key.

        self.canvas.bind_all("<Return>", self.selectionHandler)
        self.canvas.bind_all("<Shift-KeyPress>", self.selectionHandler)
        self.canvas.bind_all("<Control-KeyPress>", self.selectionHandler)
        self.canvas.bind_all("<Control-KeyRelease>", self.selectionHandler)
        self.canvas.bind_all("<KeyPress>", self.selectionHandler)
        self.canvas.bind_all("<KeyRelease>", self.selectionHandler)
        self.canvas.bind_all("<Shift-KeyRelease>", self.selectionHandler)

        self.canvas.bind_all("<ButtonPress-1>", self.selectionHandler) # left mouse button
        self.canvas.bind_all("<ButtonRelease-1>", self.selectionHandler) # left mouse button
        self.canvas.bind_all("<Button-4>", self.selectionHandler) # scroll up
        self.canvas.bind_all("<Button-5>", self.selectionHandler) # scroll down
        self.canvas.bind_all("<Motion>", self.selectionHandler) # mouse move
        self.canvas.bind_all("<Shift-Motion>", self.selectionHandler) # shift mouse move
        self.canvas.bind_all("<Control-Motion>", self.selectionHandler) # control mouse move

        self.offset = (0,0)
        self.scale = 1
        self.gcode = "\n".join([l for l in gcode.split("\n") if re.search(r"S([0-9\.]+)", l) or re.search(r"\s*(G0[01])\s*X([0-9\.]+)\s*Y([0-9\.]+)", l)])

        self.selecting = True
        while self.selecting:
            self.window.update()
            self.canvas.delete("all")
            self.drawGcode(gcode)
            self.drawSelection()
            time.sleep(0.01)

        return self.selection # as an example, just one rectangle from (0,0) to (100,100)


    def drawSelection(self):
        if self.selectRect is not None:
            color = "red" if self.selectionParity else "green"
            self.canvas.create_rectangle(*self.selectRect, outline=color)

        for rect in self.selection:
            parity, coords = rect
            color = "red" if parity else "green"
            print(coords)
            coords = (
                *self.printToCanvas(*coords[:2]),
                *self.printToCanvas(*coords[2:])
            )
            self.canvas.create_rectangle(*coords, outline=color)


    def selectionHandler(self, event: tkinter.Event):
        if event.type is tkinter.EventType.ButtonPress:
            if event.num == 4: # scroll up
                self.scale *= 1.02
            elif event.num == 5: # scroll down
                self.scale *= 0.98
            elif event.num == 1: # left mouse button
                print("click")
                self.clickStart = (event.x, event.y)
                self.oldOffset = self.offset
                if self.shift:
                    self.selectionParity = False
                    self.selectRect = [event.x, event.y, event.x, event.y]
                elif self.alt:
                    self.selectionParity = True
                    self.selectRect = [event.x, event.y, event.x, event.y]

        
        elif event.type is tkinter.EventType.ButtonRelease:
            print("un-click")
            if event.num == 1:
                self.clickStart = None

                selection = (
                    *self.canvasToPrint(*self.selectRect[:2]),
                    *self.canvasToPrint(*self.selectRect[2:])
                )
                selection = (self.selectionParity, selection)
                self.selection.append(selection)

                self.selectionParity = None
                self.selectRect = None

        elif event.type is tkinter.EventType.KeyPress:
            if event.keycode == 36: # Return
                self.selecting = False
            if event.keycode == 64: # Alt
                print("alt")
                self.alt = True
            if event.keycode == 50: # Shift
                print("shift")
                self.shift = True


        elif event.type is tkinter.EventType.KeyRelease:
            print(f"KeyRelease: {event.keycode}")

            if event.keycode == 64: # Alt
                print("un-alt")
                self.alt = False
            if event.keycode == 50: # Shift
                print("un-shift")
                self.shift = False


        elif event.type is tkinter.EventType.Motion:

            if self.clickStart is not None:
                if self.selectRect is not None:
                    print("Updating Coords of Rectangle")
                    self.selectRect[2:] = [event.x, event.y]
                    # self.canvas.coords(self.selectRect, [*self.clickStart, event.x, event.y])
                else:
                    dx = event.x - self.clickStart[0]
                    dy = event.y - self.clickStart[1]
                    self.offset = (self.oldOffset[0] + dx, self.oldOffset[1] + dy)


        else:
            print(f"Other")
            print(event.type)
        
        

    def drawGcode(self, gcode, position=(0,0)):

        intensity = 0.0
        for line in gcode.split("\n"):

            intensityMatch = re.search(r"S([0-9\.]+)", line)
            moveMatch = re.search(r"\s*(G0[01])\s*X([0-9\.]+)\s*Y([0-9\.]+)", line)

            if intensityMatch:
                intensity = float(intensityMatch[1])
            
            if moveMatch:
                x1,y1 = position
                x2, y2 = self.printToCanvas(float(moveMatch[2]), float(moveMatch[3]))
                # x2 = float(moveMatch[2]) * self.pixelsPerMilimeter * self.scale + self.offset[0], 
                # y2 = float(moveMatch[3]) * self.pixelsPerMilimeter * self.scale + self.offset[1]

                color = "blue" if intensity > 500 else "red"   
                self.canvas.create_line(x1,y1,x2,y2, fill=color)
                position = x2,y2
        
        self.window.update()





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
            


