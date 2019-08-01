import numpy as np
from PyQt5.QtGui import qGray, QPen
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsLineItem

from tab import Tab
from tab_constants import LINIFYTAB


class LinifyTab(Tab):
    def __init__(self, parent=None, layersModel=None):
        super().__init__(parent, layersModel)
        self.localBitmap = None

    def setupSlots(self):
        """
        define slots for buttons
        :return:
        """
        self.parent.linify.clicked.connect(self.process)
        self.parent.setDefaultsLinify.clicked.connect(self.SetDefaults)

    def SetDefaults(self):
        """
        triggered when set defaults button is clicked
        :return:
        """
        if not self.checkBitmapLoaded():
            return
        self.localBitmap = self.toBlackAndWhite(self.parent.bitmap.copy())
        bounds, sections = self.auto_find_bounds(self.localBitmap)
        self.parent.region1Linify.setValue(bounds[0])
        self.parent.region2Linify.setValue(bounds[1])
        self.parent.region3Linify.setValue(bounds[2])

    @staticmethod
    def get_id():
        return LINIFYTAB

    def ui_to_model(self):
        model = {}
        return model

    def model_to_ui(self, model):
        pass

    def process_without_signals(self):
        if not self.checkBitmapLoaded():
            return
        self.localBitmap = self.toBlackAndWhite(self.parent.bitmap.copy())
        self.makeLines(self.localBitmap)

    def process(self):
        """
        performs the bubblification
        :return:
        """
        self.process_without_signals()
        self.last_used_method.emit(self.parent.layersList.currentIndex(), self.get_id())

    def makeLines(self, image):
        # remove existing data on this layer
        self.removeOldGraphicsItems()

        group = QGraphicsItemGroup()

        sections = 4
        coordinates = []
        bounds = [self.parent.region1Linify.value(), self.parent.region2Linify.value(),
                  self.parent.region3Linify.value(), self.parent.region3Linify.value()]

        for y in range(0, image.height(), 4):
            drawing = False
            for linetype in range(sections):
                if linetype >= 1:
                    qt_y = y + linetype  # / sections
                    for x in range(image.width()):
                        grayvalue = qGray(image.pixel(x, y))
                        start_drawing = (grayvalue < bounds[linetype]) and not drawing
                        if start_drawing:
                            coordinates.append([[x, qt_y]])
                            drawing = True
                        stop_drawing = ((grayvalue >= bounds[linetype]) or (x == (image.width() - 1))) and drawing
                        if stop_drawing:
                            coordinates[-1].append([x, qt_y])
                            drawing = False

        group = QGraphicsItemGroup()
        for lineseg in coordinates:
            if len(lineseg) != 2 or len(lineseg[0]) != 2 or len(lineseg[1]) != 2:
                print("Unexpected lineseg: ", lineseg)
            else:
                lineitem = QGraphicsLineItem(lineseg[0][0], lineseg[0][1], lineseg[1][0], lineseg[1][1])
                pen = QPen()
                pen.setWidth(1 / sections)
                lineitem.setPen(pen)
                group.addToGroup(lineitem)

        self.addNewGraphicsItems(group)

    def auto_find_bounds(self, image):
        histogram = []
        bins = 256
        for b in range(bins):
            histogram.append(0)
        for y in range(image.height()):
            for x in range(image.width()):
                gv = qGray(image.pixel(x, y))
                histogram[gv] += 1
        sections = 4
        bounds = self.find_boundaries(sections, histogram, image)
        return bounds, sections

    def find_boundaries(self, sections, histogram, image):
        total_pixels = image.width() * image.height()
        pixels_per_section = total_pixels / sections
        percentile_bin = 1
        pixels_so_far = 0
        bounds = []
        for idx, gv in enumerate(histogram):
            pixels_so_far += histogram[idx]
            while pixels_so_far >= np.round(pixels_per_section * percentile_bin):
                bounds.append(idx)
                percentile_bin += 1
        return bounds

        # bounds = []
        # for i in range(sections):
        #     bounds.append(255 / sections * (i + 1))
        # return bounds
