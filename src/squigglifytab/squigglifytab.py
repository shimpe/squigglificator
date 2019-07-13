from math import fabs

from PyQt5.QtCore import Qt, QPersistentModelIndex
from PyQt5.QtGui import qGray, QPainterPath, QPen
from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsItemGroup
from mapping import Mapping
from tab import Tab
from utils import frange


class SquigglifyTab(Tab):
    def __init__(self, parent=None, itemsPerLayer=None):
        super().__init__(parent, itemsPerLayer)
        self.localBitmap = None

    def setupSlots(self):
        self.parent.squigglify.clicked.connect(self.process)
        self.parent.setDefaults.clicked.connect(self.SetDefaults)
        # self.parent.noOfLines.valueChanged.connect(self.Squigglify)
        # self.parent.invertColors.stateChanged.connect(self.Squigglify)
        # self.parent.verticalSquiggles.stateChanged.connect(self.Squigglify)
        # self.parent.strength.valueChanged.connect(self.Squigglify)
        # self.parent.detail.valueChanged.connect(self.Squigglify)
        # self.parent.lineWidth.valueChanged.connect(self.Squigglify)
        # self.parent.maxBrightness.valueChanged.connect(self.Squigglify)
        # self.parent.minBrightness.valueChanged.connect(self.Squigglify)
        # self.parent.minStepSize.valueChanged.connect(self.Squigglify)
        # self.parent.maxStepSize.valueChanged.connect(self.Squigglify)

    def process(self):
        if not self.checkBitmapLoaded():
            return
        self.localBitmap = self.parent.bitmap.copy()
        self.makeSquiggles(self.toBlackAndWhite(self.localBitmap))

    def SetDefaults(self):
        self.parent.noOfLines.setValue(200)
        self.parent.invertColors.setCheckState(Qt.Unchecked)
        self.parent.verticalSquiggles.setCheckState(Qt.Unchecked)
        self.parent.strength.setValue(5)
        self.parent.detail.setValue(5)
        self.parent.lineWidth.setValue(1)
        self.parent.maxBrightness.setValue(255)
        self.parent.minBrightness.setValue(0)
        layerId = self.parent.layersList.currentIndex()
        self.parent.layersModel.itemFromIndex(layerId).setCheckState(Qt.Checked)
        self.parent.minStepSize.setValue(1)
        self.parent.maxStepSize.setValue(10)

    def makeSquiggles(self, image):
        noOfLines = self.parent.noOfLines.value()
        height = image.height()
        width = image.width()
        amplitude = self.parent.strength.value()
        strokeWidth = self.parent.lineWidth.value()
        detail = self.parent.detail.value()
        invertColors = self.parent.invertColors.checkState() == Qt.Checked
        verticalSquiggles = self.parent.verticalSquiggles.checkState() == Qt.Checked
        layerId = QPersistentModelIndex(self.parent.layersList.currentIndex())
        maxBrightness = self.parent.maxBrightness.value()
        minBrightness = self.parent.minBrightness.value()
        if layerId not in self.itemsPerLayer:
            self.itemsPerLayer[layerId] = None
        if self.itemsPerLayer[layerId] is not None:
            self.parent.scene.removeItem(self.itemsPerLayer[layerId])
        group = QGraphicsItemGroup()
        finalRow = False
        # TODO: too much code duplication!
        if not verticalSquiggles:
            scaledystep = max(1, height / noOfLines)
            for y in frange(0, height, scaledystep):
                if fabs(y - height) < 1e-3 or y >= height:
                    finalRow = True
                x = 0
                minStepSize = self.parent.minStepSize.value()
                maxStepSize = self.parent.maxStepSize.value()
                disturbance_direction = -1
                prevX = 0
                prevY = y
                while x < width:
                    disturbance_direction = -disturbance_direction
                    grayvalue = 255 - qGray(image.pixel(x, y))
                    if invertColors:
                        grayvalue = 255 - grayvalue
                    stepSize = Mapping.linexp(grayvalue, 0, 255, maxStepSize, minStepSize)
                    stepSize = Mapping.linlin(stepSize, 1, 10, 1, 10 / detail)
                    amplitudeSize = Mapping.linlin(grayvalue, 0, 255, 0, amplitude)
                    if x == 0:
                        path = QPainterPath()
                        path.moveTo(x, y)
                    x = prevX + stepSize
                    newY = prevY + amplitudeSize * disturbance_direction
                    if maxBrightness > (255 - grayvalue) > minBrightness:
                        path.quadTo((prevX + x) / 2, newY, x, prevY)
                    else:
                        path.moveTo(x, prevY)
                    if x >= width:
                        item = QGraphicsPathItem(path)
                        pen = QPen()
                        pen.setWidth(strokeWidth)
                        item.setPen(pen)
                        group.addToGroup(item)
                    prevX = x
                    prevY = newY
                if finalRow:
                    break
        else:
            scaledxstep = max(1, width / noOfLines)
            for x in frange(0, width, scaledxstep):
                if fabs(x - width) < 1e-3 or x >= width:
                    finalRow = True
                y = 0
                minStepSize = 1
                maxStepSize = 10
                disturbance_direction = -1
                prevX = x
                prevY = 0
                while y < height:
                    disturbance_direction = -disturbance_direction
                    grayvalue = 255 - qGray(image.pixel(x, y))
                    if invertColors:
                        grayvalue = 255 - grayvalue
                    stepSize = Mapping.linexp(grayvalue, 0, 255, maxStepSize, minStepSize)
                    stepSize = Mapping.linlin(stepSize, 1, 10, 1, 10 / detail)
                    amplitudeSize = Mapping.linlin(grayvalue, 0, 255, 0, amplitude)
                    if y == 0:
                        path = QPainterPath()
                        path.moveTo(x, y)
                    y = prevY + stepSize
                    newX = prevX + amplitudeSize * disturbance_direction
                    if maxBrightness > (255 - grayvalue) > minBrightness:
                        path.quadTo(newX, (prevY + y) / 2, prevX, y)
                    else:
                        path.moveTo(x, prevY)
                    if y >= height:
                        item = QGraphicsPathItem(path)
                        pen = QPen()
                        pen.setWidth(strokeWidth)
                        item.setPen(pen)
                        group.addToGroup(item)
                    prevX = newX
                    prevY = y
                if finalRow:
                    break
        self.parent.scene.addItem(group)
        self.itemsPerLayer[layerId] = group
