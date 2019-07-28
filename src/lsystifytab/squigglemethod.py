import numpy as np
from PyQt5.QtGui import QPainterPath, QPen
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsPathItem

from circle import Circle
from mapping import Mapping


class SquiggleMethod(object):
    """
    class to represent how to convert LSystem overlayed on bitmap to squiggles
    """

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

    def step(self, x, y, direction, brightness):
        """
        step is called many times while iterating over the loaded bitmap
        in each step we calculate a squiggle based on position x,y with given brightness
        in the bitmap. direction is a direction vector indicating what direction we are
        moving in.

        calculate a new squiggle in the circle generation process
        :param x: x pos in bitmap that calculation should be based on
        :param y: y pos in bitmap that calculation should be based on
        :param direction: in what direction are we moving?
        :param brightness: gray value in the bitmap at x,y
        :return: potentially modified step size
        """
        stepSize = Mapping.linexp(brightness, 0, 255, self.minStepSize, self.maxStepSize)
        stepSize = Mapping.linlin(stepSize, 1, 10, 1, 10 / self.detail)
        self.previous_stepsize = stepSize
        amplitudeSize = Mapping.linlin(brightness, 0, 255, self.strength, 0)
        if self.prevPos is None:
            self.path = QPainterPath()
            self.path.moveTo(x, y)
            self.prevPos = np.array([[x, ], [y, ]])
        else:
            newPos = np.array([[x, ], [y, ]])
            dirx = direction[0][0]
            diry = direction[1][0]
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

    def skip(self, x, y, direction, brightness):
        """
        similar to step, but explicitly asking to skip generation of a squiggle (e.g. because brightness constraints are not met)
        this allows the method to update its internal state to keep track of what is happening

        :param x: x pos in bitmap that the calculation should be based on
        :param y: x pos in bitmap that the calculation should be based on
        :param direction: direction we were moving in
        :param brightness: gray value of x,y in bitmap
        :return: potentially modified step size
        """
        if self.prevPos is None:
            self.path = QPainterPath()
            self.path.moveTo(x, y)
        else:
            self.path.moveTo(x, y)
        self.prevPos = np.array([[x, ], [y, ]])
        return int(self.previous_stepsize)

    def finish(self):
        """
        return the wrapped up result of the calculations
        :return: qgraphicsitemgroup
        """
        item = QGraphicsPathItem(self.path)
        pen = QPen()
        pen.setWidth(self.strokeWidth)
        item.setPen(pen)
        self.group.addToGroup(item)
        self.prevPos = None
        return self.group
