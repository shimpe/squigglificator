from PyQt5.QtGui import qGray, QColor, QImage

class Tab(object):
    def __init__(self, parent=None, itemsPerLayer=None):
        self.parent = parent
        self.itemsPerLayer = itemsPerLayer

    def toBlackAndWhite(self, image):
        newImage = QImage(image)
        for ii in range(newImage.width()):
            for jj in range(newImage.height()):
                gray = qGray(newImage.pixel(ii, jj))
                newImage.setPixel(ii, jj, QColor(gray, gray, gray).rgb())

        return newImage