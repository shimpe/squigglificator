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
from simplification.cutil import simplify_coords


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
        self.parent.includeContoursHatchify.setCheckState(Qt.Checked)
        self.parent.includeHatchingHatchify.setCheckState(Qt.Checked)
        self.parent.hatchSizeHatchify.setValue(16)
        self.parent.contourSimplificationHatchify.setValue(2)
        self.parent.maxGVHorizontalHatchingHatchify.setValue(144)
        self.parent.maxGVDenseHorizontalHatchingHatchify.setValue(64)
        self.parent.maxGVCrossHatchingHatchify.setValue(16)
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
        model = {'includeContours'        : int(self.parent.includeContoursHatchify.checkState()),
                 'includeHatching' : int(self.parent.includeHatchingHatchify.checkState()),
                 'hatchSize'    : self.parent.hatchSizeHatchify.value(),
                 'contourSimplification'    : self.parent.contourSimplificationHatchify.value(),
                 'horGVHatching' : self.parent.maxGVHorizontalHatchingHatchify.value(),
                 'denseHorGVHatching' : self.parent.maxGVDenseHorizontalHatchingHatchify.value(),
                 'crossGVHatching' : self.parent.maxGVCrossHatchingHatchify.value()
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
        self.parent.maxGVHorizontalHatchingHatchify.setValue(int(model['horGVHatching']))
        self.parent.maxGVDenseHorizontalHatchingHatchify.setValue(int(model['denseHorGVHatching']))
        self.parent.maxGVCrossHatchingHatchify.setValue(int(model['crossGVHatching']))

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
            contours[i] = [(v[0], v[1]) for v in contours[i]]

        for i in range(0, len(contours)):
            for j in range(0, len(contours[i])):
                contours[i][j] = int(contours[i][j][0] + 10 * noise.pnoise3(i * 0.5, j * 0.1, 1)), int(
                    contours[i][j][1] + 10 * noise.pnoise3(i * 0.5, j * 0.1, 2))

        simple_contours = [simplify_coords(c, contour_simplify) for c in contours]

        return simple_contours

    def distsum(self, *args):
        return sum([
            abs(args[i][0] - args[i - 1][0]) +\
            abs(args[i][1] - args[i - 1][1]) for i in range(1, len(args))])

    def hatch(self, IM, sc=16):
        PX = IM.load()
        width, height = IM.size
        lines = []

        maxgvhor = self.parent.maxGVHorizontalHatchingHatchify.value()
        maxgvdensehor = self.parent.maxGVDenseHorizontalHatchingHatchify.value()
        maxgvcross = self.parent.maxGVCrossHatchingHatchify.value()

        # horizontal hatches
        for y in range(0, height, sc):
            pendown = False
            for x in range(0, width, sc):
                p = PX[x,y]
                if p <= maxgvhor:
                    if not pendown:
                        lines.append([[x,y]])
                    else:
                        lines[-1].append([x,y])
                    pendown = True
                else:
                    pendown = False

        # denser horizontl
        for y in range(sc//2, height, sc):
            pendown = False
            for x in range(0, width, sc):
                if PX[x,y] <= maxgvdensehor:
                    if not pendown:
                        lines.append([[x,y]])
                    else:
                        lines[-1].append([x,y])
                    pendown = True
                else:
                    pendown = False

        # diagonal top-left
        for sy in range(0, height, sc):
            pendown = False
            for x,y in zip(range(0, width, sc), range(sy-1, -1, -sc)):
                if PX[x,y] <= maxgvcross:
                    if not pendown:
                        lines.append([[x,y]])
                    else:
                        lines[-1].append([x,y])
                    pendown = True
                else:
                    pendown = False

        # for fun top left to bottom right
        #for sy in range(0, height, sc):
        #    pendown = False
        #    for x,y in zip(range(0, width, sc), range(0, sy, sc)):
        #        if PX[x,y] <= maxgvcross:
        #            if not pendown:
        #                lines.append([[x,y]])
        #            else:
        #                lines[-1].append([x,y])
        #            pendown = True
        #        else:
        #            pendown = False

        # diagonal bottom right
        for sx in range(0, width, sc):
            pendown = False
            for x,y in zip(range(sx, width, sc), range(height-1, -1, -sc)):
                #print("x = {0}, y = {1}".format(x,y))
                if PX[x,y] <= maxgvcross:
                    if not pendown:
                        lines.append([[x,y]])
                    else:
                        lines[-1].append([x,y])
                    pendown = True
                else:
                    pendown = False

        # for fun topleft to bottomright
        #for sx in range(0, width, sc):
        #    pendown = False
        #    for x,y in zip(range(sx, width, sc), range(0, height, sc)):
        #        #print("x = {0}, y = {1}".format(x,y))
        #        if PX[x,y] <= maxgvcross:
        #            if not pendown:
        #                lines.append([[x,y]])
        #            else:
        #                lines[-1].append([x,y])
        #            pendown = True
        #        else:
        #            pendown = False

        self.add_noise(lines, sc)

        return lines

    def add_noise(self, lines, sc):
        for i in range(len(lines)):
            for j in range(len(lines[i])):
                lines[i][j][0] = (lines[i][j][0] + sc * noise.pnoise3(i * 0.5, j * 0.1, 1))
                lines[i][j][1] = (lines[i][j][1] + sc * noise.pnoise3(i * 0.5, j * 0.1, 1))

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
        #print("image width = {0}, image height = {1}".format(image.width(), image.height()))
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
            lines += self.getcontours(ctimage, contour_simplify)
        if draw_hatch:
            lines += self.hatch(ctimage, hatch_size)

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
