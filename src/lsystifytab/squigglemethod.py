import numpy as np
from circle import Circle
from PyQt5.QtGui import QPainterPath, QPen
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsPathItem

from mapping import Mapping


class SquiggleMethod(object):
    def __init__(self, minBrightness, maxBrightness, strength, detail, minStepSize, maxStepSize, clipToBitmap,
                 strokeWidth, imageWidth, imageHeight):
        self.group = QGraphicsItemGroup()
        self.path = QPainterPath()
        self.minBrightness = minBrightness
        self.maxBrightness = maxBrightness
        self.strength = strength
        self.detail = detail
        self.minStepSize = minStepSize
        self.maxStepSize = maxStepSize
        self.clipToBitmap = clipToBitmap
        self.strokeWidth = strokeWidth
        self.width = imageWidth
        self.height = imageHeight
        self.prevPos = None
        self.disturbance_direction = 1
        self.previous_stepsize = 1

    def step(self, x, y, dir, brightness):
        stepSize = Mapping.linexp(brightness, 0, 255, self.maxStepSize, self.minStepSize)
        stepSize = Mapping.linlin(stepSize, 1, 10, 1, 10 / self.detail)
        self.previous_stepsize = stepSize
        amplitudeSize = Mapping.linlin(brightness, 0, 255, self.strength, 0)
        if self.prevPos is None:
            self.path = QPainterPath()
            self.path.moveTo(x, y)
            self.prevPos = np.array([[x, ], [y, ]])
        else:
            newPos = np.array([[x, ], [y, ]])
            dirx = dir[0][0]
            diry = dir[1][0]
            ortho_dir = np.array([[-diry], [dirx]]) * self.disturbance_direction
            disturbance = ortho_dir * amplitudeSize
            disturbedPos = (self.prevPos + newPos) / 2 + disturbance
            if not self.clipToBitmap or (
                    self.clipToBitmap and not Circle(x, y, amplitudeSize).edges(self.width, self.height)):
                self.path.quadTo(disturbedPos[0][0], disturbedPos[1][0], newPos[0][0], newPos[1][0])
            else:
                self.path.moveTo(newPos[0][0], newPos[1][0])
            self.prevPos = newPos
        self.disturbance_direction = -self.disturbance_direction
        return max(int(stepSize), 1)

    def skip(self, x, y, dir, brightness):
        if self.prevPos is None:
            self.path = QPainterPath()
            self.path.moveTo(x, y)
        else:
            self.path.moveTo(x, y)
        self.prevPos = np.array([[x, ], [y, ]])
        return int(self.previous_stepsize)

    def finish(self):
        item = QGraphicsPathItem(self.path)
        pen = QPen()
        pen.setWidth(self.strokeWidth)
        item.setPen(pen)
        self.group.addToGroup(item)
        self.prevPos = None
        return self.group
