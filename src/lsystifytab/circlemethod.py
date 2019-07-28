from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsEllipseItem

from lsystifytab.circle import Circle
from mapping import Mapping


class CircleMethod(object):
    """
    class to represent how an lsystem overlayed on a bitmap is converted to a list of circles
    """
    def __init__(self, minBrightness, maxBrightness, minRadius, maxRadius, minStepSize, maxStepSize, clipToBitmap,
                 strokeWidth, imageWidth, imageHeight):
        self.group = QGraphicsItemGroup()
        self.minBrightness = minBrightness
        self.maxBrightness = maxBrightness
        self.minRadius = minRadius
        self.maxRadius = maxRadius
        self.minStepSize = minStepSize
        self.maxStepSize = maxStepSize
        self.clipToBitmap = clipToBitmap
        self.strokeWidth = strokeWidth
        self.width = imageWidth
        self.height = imageHeight

    def step(self, x, y, direction, brightness):
        """
        step is called many times while iterating over the loaded bitmap
        in each step we calculate a circle based on position x,y with given brightness
        in the bitmap. direction is a direction vector indicating what direction we are
        moving in.

        calculate a new circle in the circle generation process
        :param x: x pos in bitmap that calculation should be based on
        :param y: y pos in bitmap that calculation should be based on
        :param direction: in what direction are we moving?
        :param brightness: gray value in the bitmap at x,y
        :return: potentially modified step size
        """
        r = Mapping.linexp(brightness, self.minBrightness, self.maxBrightness, self.maxRadius, self.minRadius)
        if not r:
            r = self.minRadius
        stepsize = int(Mapping.linlin(brightness, self.minBrightness, self.maxBrightness, self.minStepSize,
                                      self.maxStepSize))
        if not self.clipToBitmap or (self.clipToBitmap and not Circle(x, y, r).edges(self.width, self.height)):
            item = QGraphicsEllipseItem(x - r, y - r, r * 2, r * 2)
            pen = QPen()
            pen.setWidth(self.strokeWidth)
            item.setPen(pen)
            self.group.addToGroup(item)
        return max(int(stepsize), 1)

    def skip(self, x, y, direction, brightness):
        """
        similar to step, but explicitly asking to skip generation of a circle (e.g. because brightness constraints are not met)
        this allows the method to update its internal state to keep track of what is happening

        :param x: x pos in bitmap that the calculation should be based on
        :param y: x pos in bitmap that the calculation should be based on
        :param direction: direction we were moving in
        :param brightness: gray value of x,y in bitmap
        :return: potentially modified step size
        """
        stepsize = int(Mapping.linlin(brightness, self.minBrightness, self.maxBrightness, self.minStepSize,
                                      self.maxStepSize))
        return max(int(stepsize), 1)

    def finish(self):
        """
        return the wrapped up result of the calculations
        :return: qgraphicsitemgroup
        """
        return self.group
