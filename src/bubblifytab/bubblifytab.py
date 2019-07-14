from random import random

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import qGray, QPen
from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsItemGroup
from scipy import spatial

from mapping import Mapping
from tab import Tab


class BubblifyTab(Tab):
    def __init__(self, parent=None, itemsPerLayer=None):
        super().__init__(parent, itemsPerLayer)
        self.localBitmap = None

    def setupSlots(self):
        self.parent.progressBarBubblify.setVisible(False)
        self.parent.bubblify.clicked.connect(self.process)
        self.parent.setDefaultsBubblify.clicked.connect(self.SetDefaults)

    def SetDefaults(self):
        minBrightness = self.parent.minBrightnessBubblify.setValue(0)
        maxBrightness = self.parent.maxBrightnessBubblify.setValue(255)
        minCircleRadius = self.parent.minRadiusBubblify.setValue(1)
        maxCircleRadius = self.parent.maxRadiusBubblify.setValue(10)
        invertColors = self.parent.invertColorsBubblify.setCheckState(Qt.Unchecked)
        minProbability = self.parent.minProbabilityBubblify.setValue(1)
        maxProbablity = self.parent.maxProbabilityBubblify.value(20)
        radiustolerance = self.parent.radiusToleranceBubblify.value(0.4)

    def process(self):
        if not self.checkBitmapLoaded():
            return
        self.localBitmap = self.toBlackAndWhite(self.parent.bitmap.copy())
        self.makeBubbles(self.localBitmap)

    def makeBubbles(self, image):
        self.parent.progressBarBubblify.setVisible(True)
        self.parent.application.processEvents()

        minBrightness = self.parent.minBrightnessBubblify.value()
        maxBrightness = self.parent.maxBrightnessBubblify.value()
        minCircleRadius = self.parent.minRadiusBubblify.value()
        maxCircleRadius = self.parent.maxRadiusBubblify.value()
        invertColors = self.parent.invertColorsBubblify.checkState() == Qt.Checked
        minProbability = self.parent.minProbabilityBubblify.value()
        maxProbablity = self.parent.maxProbabilityBubblify.value()
        radiustolerance = self.parent.radiusToleranceBubblify.value()
        strokeWidth = 1

        # remove existing data on this layer
        self.removeOldGraphicsItems()

        # first add seeding points
        print("Seeding points")
        spots = []
        circles = []
        for x in range(image.width()):
            for y in range(image.height()):
                grayvalue = qGray(image.pixel(x, y))
                if minBrightness < grayvalue < maxBrightness:
                    probability = Mapping.linexp(grayvalue, 0, 255, maxProbablity / 100, minProbability / 100)
                    addNow = random() < probability
                    if addNow:
                        spots.append([x, y])

        print("Optimizing {0} points".format(len(spots)))
        # next find out radii we can use that avoid overlap
        print("Analyzing radii")
        if len(spots):
            tree = spatial.KDTree(spots)
            for center in spots:
                x = center[0]
                y = center[1]
                grayvalue = qGray(image.pixel(x, y))
                proposed_radius = Mapping.linexp(grayvalue, minBrightness, maxBrightness, minCircleRadius,
                                                 maxCircleRadius)
                nearest_neighbor = tree.query(np.array([[x, y]]), 2)
                # print("{0} nearest to {1}".format(nearest_neighbor, [x,y]))
                if nearest_neighbor:
                    try:
                        distance = nearest_neighbor[0][0][1]
                        maxradius = np.floor(distance / 2)
                        minimum = min(proposed_radius, maxradius)
                        # print("Using minimum of proposed {0} and max {1}".format(proposed_radius, maxradius))
                        if minimum >= proposed_radius * radiustolerance:
                            circles.append((x, y, minimum))
                    except:
                        print("weird nearest neighbor: ", nearest_neighbor)

            print("Visualize")
            # next, visualize
            group = QGraphicsItemGroup()
            for c in circles:
                x = c[0]
                y = c[1]
                r = c[2]
                item = QGraphicsEllipseItem(x - r, y - r, r * 2, r * 2)
                pen = QPen()
                pen.setWidth(strokeWidth)
                item.setPen(pen)
                group.addToGroup(item)
            self.addNewGraphicsItems(group)

            self.parent.progressBarBubblify.setVisible(False)
