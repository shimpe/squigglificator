from random import random

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import qGray, QPen
from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsItemGroup
from scipy import spatial

from mapping import Mapping
from tab import Tab
from tab_constants import BUBBLIFYTAB


class BubblifyTab(Tab):
    """
    this tab implements the "Bubblify" wizard
    """

    def __init__(self, parent=None, layersModel=None):
        super().__init__(parent, layersModel)
        self.localBitmap = None

    def setupSlots(self):
        """
        define slots for buttons
        :return:
        """
        self.parent.progressBarBubblify.setVisible(False)
        self.parent.bubblify.clicked.connect(self.process)
        self.parent.setDefaultsBubblify.clicked.connect(self.SetDefaults)

    def SetDefaults(self):
        """
        triggered when set defaults button is clicked
        :return:
        """
        self.parent.minBrightnessBubblify.setValue(0)
        self.parent.maxBrightnessBubblify.setValue(255)
        self.parent.minRadiusBubblify.setValue(1)
        self.parent.maxRadiusBubblify.setValue(10)
        self.parent.invertColorsBubblify.setCheckState(Qt.Unchecked)
        self.parent.minProbabilityBubblify.setValue(1)
        self.parent.maxProbabilityBubblify.setValue(20)
        self.parent.radiusToleranceBubblify.setValue(0.4)

    def get_id(self):
        return BUBBLIFYTAB

    def ui_to_model(self):
        model = {'minRadius'      : self.parent.minRadiusBubblify.value(),
                 'maxRadius'      : self.parent.maxRadiusBubblify.value(),
                 'invertColors'   : int(self.parent.invertColors.checkState()),
                 'minProbability' : self.parent.minProbabilityBubblify.value(),
                 'maxProbability' : self.parent.maxProbabilityBubblify.value(),
                 'radiusTolerance': self.parent.radiusToleranceBubblify.value(),
                 'minBrightness'  : self.parent.minBrightnessBubblify.value(),
                 'maxBrightness'  : self.parent.maxBrightnessBubblify.value()}
        return model

    def model_to_ui(self, model):
        self.parent.minRadiusBubblify.setValue(int(model['minRadius']))
        self.parent.maxRadiusBubblify.setValue(int(model['maxRadius']))
        self.parent.invertColors.setCheckState(int(model['invertColors']))
        self.parent.minProbabilityBubblify.setValue(float(model['minProbability']))
        self.parent.maxProbabilityBubblify.setValue(float(model['maxProbability']))
        self.parent.radiusToleranceBubblify.setValue(float(model['radiusTolerance']))
        self.parent.minBrightnessBubblify.setValue(int(model['minBrightness']))
        self.parent.maxBrightnessBubblify.setValue(int(model['maxBrightness']))

    def process_without_signals(self):
        if not self.checkBitmapLoaded():
            return
        self.localBitmap = self.toBlackAndWhite(self.parent.bitmap.copy())
        self.makeBubbles(self.localBitmap)
        
    def process(self):
        """
        performs the bubblification
        :return:
        """
        self.process_without_signals()
        self.last_used_method.emit(self.parent.layersList.currentIndex(), self.get_id())

    def makeBubbles(self, image):
        """
        helper method for bubblification (contains the actual calculations)
        :param image:
        :return:
        """
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
                if invertColors:
                    grayvalue = 255 - grayvalue
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
