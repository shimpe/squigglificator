from PyQt5.QtCore import QPersistentModelIndex
from PyQt5.QtGui import qGray, QColor, QImage
from PyQt5.QtWidgets import QMessageBox


class Tab(object):
    def __init__(self, parent=None, itemsPerLayer=None):
        self.parent = parent
        self.itemsPerLayer = itemsPerLayer

    def after_load_bitmap(self):
        pass

    def on_quit(self):
        pass

    def toBlackAndWhite(self, image):
        newImage = QImage(image)
        for ii in range(newImage.width()):
            for jj in range(newImage.height()):
                gray = qGray(newImage.pixel(ii, jj))
                newImage.setPixel(ii, jj, QColor(gray, gray, gray).rgb())

        return newImage

    def checkBitmapLoaded(self):
        if self.parent.bitmap is None:
            msgBox = QMessageBox()
            msgBox.setText("Please load bitmap first.")
            msgBox.exec()
            return False
        return True

    def removeOldGraphicsItems(self):
        layerId = QPersistentModelIndex(self.parent.layersList.currentIndex())
        if layerId not in self.itemsPerLayer:
            self.itemsPerLayer[layerId] = None
        if self.itemsPerLayer[layerId] is not None:
            self.parent.scene.removeItem(self.itemsPerLayer[layerId])

    def addNewGraphicsItems(self, group):
        self.parent.scene.addItem(group)
        layerId = QPersistentModelIndex(self.parent.layersList.currentIndex())
        self.itemsPerLayer[layerId] = group
