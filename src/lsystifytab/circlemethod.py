from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsEllipseItem

from circle import Circle
from mapping import Mapping


class CircleMethod(object):
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

    def step(self, x, y, dir, brightness):
        r = Mapping.linexp(brightness, self.minBrightness, self.maxBrightness, self.maxRadius, self.minRadius)
        stepsize = int(Mapping.linlin(brightness, self.minBrightness, self.maxBrightness, self.minStepSize,
                                      self.maxStepSize))
        if not self.clipToBitmap or (self.clipToBitmap and not Circle(x, y, r).edges(self.width, self.height)):
            item = QGraphicsEllipseItem(x - r, y - r, r * 2, r * 2)
            pen = QPen()
            pen.setWidth(self.strokeWidth)
            item.setPen(pen)
            self.group.addToGroup(item)
        return max(int(stepsize), 1)

    def skip(self, x, y, dir, brightness):
        stepsize = int(Mapping.linlin(brightness, self.minBrightness, self.maxBrightness, self.minStepSize,
                                      self.maxStepSize))
        return max(int(stepsize), 1)

    def finish(self):
        return self.group
