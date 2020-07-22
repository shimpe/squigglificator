from math import fabs, sqrt
import numpy as np
from random import random

from PyQt5.QtCore import Qt
from PyQt5.QtGui import qGray, QPainterPath, QPen, QColor
from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsItemGroup

from mapping import Mapping
from tab import Tab
from tab_constants import RANDWALKTAB
from utils import frange
from itertools import combinations
from simplification.cutil import simplify_coords

class RandomWalkTabTab(Tab):
    def __init__(self, parent=None, layersModel=None):
        super().__init__(parent, layersModel)
        self.localBitmap = None

    def setupSlots(self):
        """
        make the buttons do something
        :return:
        """
        self.parent.walkify.clicked.connect(self.process)
        self.parent.setDefaultsWalkify.clicked.connect(self.SetDefaults)


    def process_without_signals(self):
        if not self.checkBitmapLoaded():
            return
        self.localBitmap = self.parent.bitmap.copy()
        self.randomWalk(self.toBlackAndWhite(self.localBitmap))

    def process(self):
        """
        called to calculate the squiggles from a bitmap
        :return:
        """
        self.process_without_signals()
        self.last_used_method.emit(self.parent.layersList.currentIndex(), self.get_id())

    def SetDefaults(self):
        """
        called when user clicks set defaults button
        :return:
        """
        self.parent.noOfWalksWalkify.setValue(5)
        self.parent.noOfLineSegmentsWalkify.setValue(30000)
        self.parent.lineWidthWalkify.setValue(1)
        self.parent.maxBrightnessWalkify.setValue(255)
        self.parent.minBrightnessWalkify.setValue(0)
        layerId = self.parent.layersList.currentIndex()
        self.parent.layersModel.itemFromIndex(layerId).setCheckState(Qt.Checked)
        self.parent.localBrightnessAdjustmentWalkify.setValue(8)
        self.parent.reductionNeighborhoodWalkify.setValue(5)
        self.parent.polylineSimplificationToleranceWalkify.setValue(10)
        self.parent.useSmootherShapesWalkify.setCheckState(Qt.Checked)

    @staticmethod
    def get_id():
        return RANDWALKTAB

    def ui_to_model(self):
        """
        summarize ui controls in a model (dict of key->value)
        :return: model
        """
        model = {'noOfWalks'        : self.parent.noOfWalksWalkify.value(),
                 'noOfLineSegments' : self.parent.noOfLineSegmentsWalkify.value(),
                 'lineWidth'        : self.parent.lineWidthWalkify.value(),
                 'minBrightness'    : self.parent.minBrightnessWalkify.value(),
                 'maxBrightness'    : self.parent.maxBrightnessWalkify.value(),
                 'localBrightnessAdjustment'      : self.parent.localBrightnessAdjustmentWalkify.value(),
                 'reductionNeighborhood' : self.parent.reductionNeighborhoodWalkify.value(),
                 'polylineSimplificationTolerance' : self.parent.polylineSimplificationToleranceWalkify.value(),
                 'useSmootherShapes' : int(self.parent.useSmootherShapesWalkify.checkState())}
        return model

    def model_to_ui(self, model):
        """
        set model values into ui controls
        :param model: model
        :return:
        """
        self.parent.noOfWalksWalkify.setValue(int(model['noOfWalks']))
        self.parent.noOfLineSegmentsWalkify.setValue(int(model['noOfLineSegments']))
        self.parent.lineWidthWalkify.setValue(int(model['lineWidth']))
        self.parent.minBrightnessWalkify.setValue(int(model['minBrightness']))
        self.parent.maxBrightnessWalkify.setValue(int(model['maxBrightness']))
        self.parent.localBrightnessAdjustmentWalkify.setValue(int(model['localBrightnessAdjustment']))
        self.parent.reductionNeighborhoodWalkify.setValue(int(model['reductionNeighborhood']))
        self.parent.polylineSimplificationToleranceWalkify.setValue(int(model['polylineSimplificationTolerance']))
        self.parent.useSmootherShapesWalkify.setCheckState(model['useSmootherShapes'])

    def lighten_one_pixel(self, image, offset, x, y):
        currcolor = qGray(image.pixel(x, y))
        newcolor = Mapping.clip_value(currcolor + offset, 0, 255)
        image.setPixelColor(x, y, QColor(newcolor, newcolor, newcolor))

    def lighten_area_around(self, image, offset, x, y):
        half_radius = self.parent.reductionNeighborhoodWalkify.value()
        min_x = Mapping.clip_value(x - half_radius, half_radius, image.width() - half_radius)
        max_x = Mapping.clip_value(x + half_radius, half_radius, image.width() - half_radius)
        min_y = Mapping.clip_value(y - half_radius, half_radius, image.height() - half_radius)
        max_y = Mapping.clip_value(y + half_radius, half_radius, image.height() - half_radius)
        adjustbrightness = self.parent.localBrightnessAdjustmentWalkify.value()
        myset = set()
        for s in range(int(round(half_radius/2))):
            myset.add(s)
            myset.add(-s)
        for comb in combinations(myset, 2):
            inv_distance = 2*max(myset) - (abs(comb[0]) + abs(comb[1]))
            modfactor = half_radius*inv_distance
            self.lighten_one_pixel(image, adjustbrightness * modfactor, x + comb[0], y + comb[1])
        for el in myset:
            inv_distance = 2 * max(myset) - (2*abs(el))
            modfactor = half_radius * inv_distance
            self.lighten_one_pixel(image, adjustbrightness * modfactor, x + el, y + el)

    def find_darkest(self, image):
        darkest_value = 256
        darkest_x = 0
        darkest_y = 0
        half_radius = self.parent.reductionNeighborhoodWalkify.value()
        for x in range(half_radius, image.width() - half_radius, 1):
            for y in range(half_radius, image.height() - half_radius, 1):
                currcolor = qGray(image.pixel(x,y))
                if currcolor < darkest_value:
                    darkest_x = x
                    darkest_y = y
                    darkest_value = currcolor
        return darkest_x, darkest_y

    def find_darkest_neighbor(self, image, cx, cy):
        darkest_neighbor = 256
        half_radius = self.parent.reductionNeighborhoodWalkify.value()
        min_x = Mapping.clip_value(cx - half_radius, half_radius, image.width() - half_radius)
        min_y = Mapping.clip_value(cy - half_radius, half_radius, image.height() - half_radius)
        max_x = Mapping.clip_value(cx + half_radius, half_radius, image.width() - half_radius)
        max_y = Mapping.clip_value(cy + half_radius, half_radius, image.height() - half_radius)

        for x in range(min_x, max_x+1):
            for y in range(min_y, max_y+1):
                distance = sqrt((x-cx)**2 + (y-cy)**2)
                if distance < half_radius:
                    currcolor = qGray(image.pixel(x,y)) + random()*0.01
                    if currcolor < darkest_neighbor:
                        darkest_x = x
                        darkest_y = y
                        darkest_neighbor = currcolor
        return darkest_x, darkest_y, darkest_neighbor

    def randomWalk(self, image):
        """
        actual calculations
        :param image: bitmap to squigglify
        :return:
        """
        self.removeOldGraphicsItems()
        group = QGraphicsItemGroup()
        no_of_walks = self.parent.noOfWalksWalkify.value()
        coordinates = {}
        self.applyThreshold(image)
        for w in range(no_of_walks):
            x, y = self.find_darkest(image)
            x, y, color = self.find_darkest_neighbor(image, x, y)
            coordinates[w] = np.array([[x,y]])
            no_of_line_segments = self.parent.noOfLineSegmentsWalkify.value()
            adjustbrightness = self.parent.localBrightnessAdjustmentWalkify.value()
            stroke_width = self.parent.lineWidthWalkify.value()
            for s in range(0, no_of_line_segments):
                dx, dy, dc = self.find_darkest_neighbor(image, x, y)
                self.lighten_area_around(image, adjustbrightness, dx, dy)
                x,y = dx, dy
                coordinates[w] = np.append(coordinates[w], [[x, y]], axis=0)

        for w in range(no_of_walks):
            coordinates[w] = simplify_coords(coordinates[w], self.parent.polylineSimplificationToleranceWalkify.value())

        for w in range(no_of_walks):
            path = QPainterPath()
            in_the_middle_of_a_quad = False
            for idx, c in enumerate(coordinates[w]):
                quad = self.parent.useSmootherShapesWalkify.checkState() == Qt.Checked
                if not quad:
                    if idx == 0:
                        path.moveTo(coordinates[w][idx][0], coordinates[w][idx][1])
                    else:
                        path.lineTo(coordinates[w][idx][0], coordinates[w][idx][1])
                else:
                    if idx == 0:
                        path.moveTo(coordinates[w][idx][0], coordinates[w][idx][1])
                    elif idx % 2 == 1:
                        middlex, middley = coordinates[w][idx][0], coordinates[w][idx][1]
                        in_the_middle_of_a_quad = True
                    else:
                        path.quadTo(middlex, middley, coordinates[w][idx][0], coordinates[w][idx][1])
                        in_the_middle_of_a_quad = False

            if in_the_middle_of_a_quad:
                path.lineTo(middlex, middley)

            item = QGraphicsPathItem(path)
            pen = QPen()
            pen.setWidth(stroke_width)
            item.setPen(pen)
            group.addToGroup(item)

        self.addNewGraphicsItems(group)

    def applyThreshold(self, image):
        minBrightness = self.parent.minBrightnessWalkify.value()
        maxBrightness = self.parent.maxBrightnessWalkify.value()
        if minBrightness != 0 or maxBrightness != 255:
            for x in range(image.width()):
                for y in range(image.height()):
                    currcolor = qGray(image.pixel(x, y))
                    if currcolor <= minBrightness:
                        image.setPixelColor(x, y, QColor(255, 255, 255))
                    if currcolor >= maxBrightness:
                        image.setPixelColor(x, y, QColor(255, 255, 255))

