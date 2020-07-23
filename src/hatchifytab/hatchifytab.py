from math import fabs, sqrt
import numpy as np

from PyQt5.QtCore import Qt
from PyQt5.QtGui import qGray, QPainterPath, QPen, QColor
from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsItemGroup
from tab import Tab
from tab_constants import HATCHIFYTAB
from imageconvert import qimage_to_pil_image
from PIL import Image, ImageOps
import cv2
import noise

class HatchifyTab(Tab):
    def __init__(self, parent=None, layersModel=None):
        super().__init__(parent, layersModel)
        self.localBitmap = None

    def setupSlots(self):
        """
        make the buttons do something
        :return:
        """
        self.parent.hatchify.clicked.connect(self.process)
        self.parent.setDefaultsHatchify.clicked.connect(self.SetDefaults)


    def process_without_signals(self):
        if not self.checkBitmapLoaded():
            return
        self.localBitmap = self.parent.bitmap.copy()
        self.hatchify(self.toBlackAndWhite(self.localBitmap))

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
        self.parent.includeContoursHatchify.setValue(1)
        self.parent.includeHatchingHatchify.setValue(1)
        self.parent.hatchSizeHatchify.setValue(16)
        self.parent.contourSimplificationHatchify.setValue(2)
        layerId = self.parent.layersList.currentIndex()
        self.parent.layersModel.itemFromIndex(layerId).setCheckState(Qt.Checked)

    @staticmethod
    def get_id():
        return HATCHIFYTAB

    def ui_to_model(self):
        """
        summarize ui controls in a model (dict of key->value)
        :return: model
        """
        model = {'includeContours'        : int(self.parent.includeContoursHatchify.checkState() == Qt.Checked),
                 'includeHatching' : int(self.parent.includeHatchingHatchify.checkState() == Qt.Checked),
                 'hatchSize'    : self.parent.hatchSizeHatchify.value(),
                 'contourSimplification'    : self.parent.contourSimplificationHatchify.value(),
                 }
        return model

    def model_to_ui(self, model):
        """
        set model values into ui controls
        :param model: model
        :return:
        """
        self.parent.includeContoursHatchify.setCheckState(int(model['includeContours']))
        self.parent.includeHatchingHatchify.setCheckState(int(model['includeHatching']))
        self.parent.hatchSizeHatchify.setValue(int(model['hatchSize']))
        self.parent.contourSimplificationHatchify.setValue(int(model['contourSimplification']))

    def find_edges(self, IM):
        im = np.array(IM)
        im = cv2.GaussianBlur(im, (3, 3), 0)
        im = cv2.Canny(im, 100, 200)
        IM = Image.fromarray(im)
        return IM.point(lambda p: p > 128 and 255)

    def getdots(self, IM):
        PX = IM.load()
        dots = []
        w, h = IM.size
        for y in range(h - 1):
            row = []
            for x in range(1, w):
                if PX[x, y] == 255:
                    x0 = x
                    while x < w and PX[x,y] == 255:
                        x = x+1
                    row.append((x0, x-x0))
            dots.append(row)
        return dots

    def connectdots(self, dots):
        contours = []
        for y in range(len(dots)):
            for x, v in dots[y]:
                if v > -1:
                    if y == 0:
                        contours.append([(x, y)])
                    else:
                        closest = -1
                        cdist = 1e10
                        for x0, v0 in dots[y - 1]:
                            if abs(x0 - x) < cdist:
                                cdist = abs(x0 - x)
                                closest = x0

                        if cdist > 3:
                            contours.append([(x, y)])
                        else:
                            found = 0
                            for i in range(len(contours)):
                                if contours[i][-1] == (closest, y - 1):
                                    contours[i].append((x, y,))
                                    found = 1
                                    break
                            if found == 0:
                                contours.append([(x, y)])
            for c in contours:
                if c[-1][1] < y - 1 and len(c) < 4:
                    contours.remove(c)
        return contours

    def getcontours(self, pil_image, contour_simplify):
        pil_image = self.find_edges(pil_image)
        IM1 = pil_image.copy()
        IM2 = pil_image.rotate(-90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
        dots1 = self.getdots(IM1)
        contours1 = self.connectdots(dots1)
        dots2 = self.getdots(IM2)
        contours2 = self.connectdots(dots2)

        for i in range(len(contours2)):
            contours2[i] = [(c[1], c[0]) for c in contours2[i]]
        contours = contours1 + contours2

        for i in range(len(contours)):
            for j in range(len(contours)):
                if len(contours[i]) > 0 and len(contours[j]) > 0:
                    if self.distsum(contours[j][0], contours[i][-1]) < 8:
                        contours[i] = contours[i] + contours[j]
                        contours[j] = []

        for i in range(len(contours)):
            contours[i] = [contours[i][j] for j in range(0, len(contours[i]), 8)]

        contours = [c for c in contours if len(c) > 1]

        for i in range(0, len(contours)):
            contours[i] = [(v[0] * contour_simplify, v[1] * contour_simplify) for v in contours[i]]

        for i in range(0, len(contours)):
            for j in range(0, len(contours[i])):
                contours[i][j] = int(contours[i][j][0] + 10 * noise.pnoise3(i * 0.5, j * 0.1, 1)), int(
                    contours[i][j][1] + 10 * noise.pnoise3(i * 0.5, j * 0.1, 2))

        return contours

    def distsum(self, *args):
        return sum([
            abs(args[i][0] - args[i - 1][0]) +\
            abs(args[i][1] - args[i - 1][1]) for i in range(1, len(args))])

    def hatch(self, IM, sc=16):
        PX = IM.load()
        w, h = IM.size
        lg1 = []
        lg2 = []
        for x0 in range(w):
            for y0 in range(h):
                x = x0 * sc
                y = y0 * sc
                if PX[x0, y0] > 144:
                    pass

                elif PX[x0, y0] > 64:
                    lg1.append([(x, y + sc / 4), (x + sc, y + sc / 4)])
                elif PX[x0, y0] > 16:
                    lg1.append([(x, y + sc / 4), (x + sc, y + sc / 4)])
                    lg2.append([(x + sc, y), (x, y + sc)])

                else:
                    lg1.append([(x, y + sc / 4), (x + sc, y + sc / 4)])
                    lg1.append([(x, y + sc / 2 + sc / 4), (x + sc, y + sc / 2 + sc / 4)])
                    lg2.append([(x + sc, y), (x, y + sc)])

        lines = [lg1, lg2]
        for k in range(0, len(lines)):
            for i in range(0, len(lines[k])):
                for j in range(0, len(lines[k])):
                    if lines[k][i] != [] and lines[k][j] != []:
                        if lines[k][i][-1] == lines[k][j][0]:
                            lines[k][i] = lines[k][i] + lines[k][j][1:]
                            lines[k][j] = []
            lines[k] = [l for l in lines[k] if len(l) > 0]
        lines = lines[0] + lines[1]

        for i in range(0, len(lines)):
            for j in range(0, len(lines[i])):
                lines[i][j] = int(lines[i][j][0] + sc * noise.pnoise3(i * 0.5, j * 0.1, 1)), int(
                    lines[i][j][1] + sc * noise.pnoise3(i * 0.5, j * 0.1, 2)) - j
        return lines

    def sortlines(self, lines):
        clines = lines[:]
        slines = []
        if clines:
            slines = [clines.pop(0)]
            while clines != []:
                x, s, r = None, 1e10, False
                for l in clines:
                    d = self.distsum(l[0], slines[-1][-1])
                    dr = self.distsum(l[-1], slines[-1][-1])
                    if d < s:
                        x, s, r = l[:], d, False
                    if dr < s:
                        x, s, r = l[:], s, True

                clines.remove(x)
                if r:
                    x = x[::-1]
                slines.append(x)
        return slines

    def hatchify(self, image):
        """
        actual calculations
        :param image: bitmap to squigglify
        :return:
        """
        print("image width = {0}, image height = {1}".format(image.width(), image.height()))
        ctimage = ImageOps.autocontrast(qimage_to_pil_image(image).convert("L"), 10)
        draw_contours = self.parent.includeContoursHatchify.checkState() == Qt.Checked
        draw_hatch = self.parent.includeHatchingHatchify.checkState() == Qt.Checked
        contour_simplify = self.parent.contourSimplificationHatchify.value()
        hatch_size = self.parent.hatchSizeHatchify.value()
        resolution = image.width()
        w, h = image.width(), image.height()
        aspect_ratio = h/w

        lines = []
        inv_resize_factor = (1, 1)
        if draw_contours:
            contour_resize_factor = (resolution // contour_simplify, int(resolution * aspect_ratio) // contour_simplify)
            print("contour resize factor {0}".format(contour_resize_factor))
            lines += self.getcontours(ctimage.resize(contour_resize_factor), contour_simplify)
        if draw_hatch:
            hatch_resize_factor = (resolution // hatch_size, int(resolution * aspect_ratio)//hatch_size)
            print("hatch resize factor {0}".format(hatch_resize_factor))
            lines += self.hatch(ctimage.resize(hatch_resize_factor), hatch_size)

        lines = self.sortlines(lines)

        self.removeOldGraphicsItems()
        group = QGraphicsItemGroup()
        for line in lines:
            path = QPainterPath()
            for point_idx, point in enumerate(line):
                if point_idx == 0:
                    path.moveTo(point[0], point[1])
                else:
                    path.lineTo(point[0], point[1])
            item = QGraphicsPathItem(path)
            group.addToGroup(item)

        self.addNewGraphicsItems(group)
