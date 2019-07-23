import re

import numpy as np
from PyQt5.QtCore import Qt, QPersistentModelIndex
from PyQt5.QtGui import qGray, QPainterPath, QPen
from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsItemGroup
from skimage.draw import line

from lsystifytab.circlemethod import CircleMethod
from lsystifytab.lsystem import LSystem
from lsystifytab.lsysteminterpreter import LSystemInterpreter
from lsystifytab.squigglemethod import SquiggleMethod
from tab import Tab


def rotmatrix(theta):
    c, s = np.cos(theta), np.sin(theta)
    R = np.array(((c, -s), (s, c)))
    return R


class LSystifyTab(Tab):
    def __init__(self, parent=None, itemsPerLayer=None):
        super().__init__(parent, itemsPerLayer)
        self.localBitmap = None
        self.lsystem = LSystem()
        self.lsysteminterpreter = LSystemInterpreter()

    def setupSlots(self):
        self.parent.lsystify.clicked.connect(self.process)
        self.parent.drawLSystemLSystify.clicked.connect(self.visualize)
        self.parent.methodLSystify.currentTextChanged.connect(self.OnMethod)
        self.parent.presetLSystify.currentTextChanged.connect(self.OnPreset)
        self.OnMethod("Circles")
        self.OnPreset("Hilbert")

    def add_dir(self, gs):
        gs["x,y"] = gs["x,y"] + gs["dir"]
        gs["pts"].append((gs["x,y"], gs["dir"]))
        return gs

    def rotate_cw(self, gs):
        R = rotmatrix(np.radians(self.minAngle))
        gs["dir"] = np.matmul(R, gs["dir"])
        return gs

    def rotate_ccw(self, gs):
        R = rotmatrix(np.radians(self.plusAngle))
        gs["dir"] = np.matmul(R, gs["dir"])
        return gs

    def OnPreset(self, text):
        if text == "Hilbert":
            self.parent.iterationsLSystify.setValue(6)
            self.parent.axiomLSystify.setText("R")
            self.parent.rulesLSystify.setText("L = +RF-LFL-FR+; R = -LF+RFR+FL-")
            self.parent.constantsLSystify.setText("L; R")
            self.parent.invertColorsLSystify.setCheckState(Qt.Unchecked)
            self.parent.initialAngleLSystify.setValue(0)
            self.parent.minAngleLSystify.setValue(-90)
            self.parent.plusAngleLSystify.setValue(90)
        elif text == "Hilbert II":
            self.parent.iterationsLSystify.setValue(4)
            self.parent.axiomLSystify.setText("X")
            self.parent.rulesLSystify.setText("X = XFYFX + F + YFXFY - F - XFYFX; Y = YFXFY - F - XFYFX + F + YFXFY")
            self.parent.constantsLSystify.setText("")
            self.parent.invertColorsLSystify.setCheckState(Qt.Unchecked)
            self.parent.initialAngleLSystify.setValue(0)
            self.parent.minAngleLSystify.setValue(-90)
            self.parent.plusAngleLSystify.setValue(90)
        elif text == "Peano-Gosper":
            self.parent.iterationsLSystify.setValue(4)
            self.parent.axiomLSystify.setText("FX")
            self.parent.rulesLSystify.setText("X=X+YF++YF-FX--FXFX-YF+; Y=-FX+YFYF++YF+FX--FX-Y")
            self.parent.constantsLSystify.setText("")
            self.parent.invertColorsLSystify.setCheckState(Qt.Unchecked)
            self.parent.initialAngleLSystify.setValue(0)
            self.parent.minAngleLSystify.setValue(-60)
            self.parent.plusAngleLSystify.setValue(60)
        elif text == "Peano":
            self.parent.iterationsLSystify.setValue(4)
            self.parent.axiomLSystify.setText("F")
            self.parent.rulesLSystify.setText("F=F+F-F-F-F+F+F+F-F")
            self.parent.constantsLSystify.setText("")
            self.parent.invertColorsLSystify.setCheckState(Qt.Unchecked)
            self.parent.initialAngleLSystify.setValue(0)
            self.parent.minAngleLSystify.setValue(-90)
            self.parent.plusAngleLSystify.setValue(90)
        elif text == "Square curve":
            self.parent.iterationsLSystify.setValue(4)
            self.parent.axiomLSystify.setText("F+XF+F+XF")
            self.parent.rulesLSystify.setText("X=XF-F+F-XF+F+XF-F+F-X")
            self.parent.constantsLSystify.setText("")
            self.parent.invertColorsLSystify.setCheckState(Qt.Unchecked)
            self.parent.initialAngleLSystify.setValue(0)
            self.parent.minAngleLSystify.setValue(-90)
            self.parent.plusAngleLSystify.setValue(90)
        elif text == "Sierpinsky triangle":
            self.parent.iterationsLSystify.setValue(6)
            self.parent.axiomLSystify.setText("FXF--FF--FF")
            self.parent.rulesLSystify.setText("F=FF; X=--FXF++FXF++FXF--")
            self.parent.constantsLSystify.setText("X")
            self.parent.invertColorsLSystify.setCheckState(Qt.Unchecked)
            self.parent.initialAngleLSystify.setValue(0)
            self.parent.minAngleLSystify.setValue(-60)
            self.parent.plusAngleLSystify.setValue(60)

    def push_state(self, gs):
        gs["posstack"] = gs["posstack"].append(gs["x,y"])
        gs["dirstack"] = gs["dirstack"].append(gs["dir"])

    def pop_state(self, gs):
        if gs["posstack"] != []:
            gs["posstack"].pop()
        if gs["dirstack"] != []:
            gs["dirstack"].pop()

    def process(self):
        if not self.checkBitmapLoaded():
            return
        self.getdata()
        self.run_lsystem()
        self.discretize_lsystem()
        pixel_order = self.discretize_lsystem()
        pixel_order.reverse()
        self.reversed_pixel_order = pixel_order
        self.localBitmap = self.parent.bitmap.copy()
        self.make(self.toBlackAndWhite(self.localBitmap))

    def make(self, image):
        self.removeOldGraphicsItems()
        if self.method == "Circles":
            methodhandler = CircleMethod(self.minBrightness, self.maxBrightness,
                                         self.minRadius, self.maxRadius,
                                         self.minStepSize, self.maxStepSize,
                                         self.clipToBitmap,
                                         self.strokeWidth,
                                         image.width(),
                                         image.height())
        elif self.method == "Squiggles":
            methodhandler = SquiggleMethod(self.minBrightness, self.maxBrightness,
                                           self.strength, self.detail,
                                           self.minStepSize, self.maxStepSize,
                                           self.clipToBitmap,
                                           self.strokeWidth,
                                           image.width(),
                                           image.height())

        pos = self.reversed_pixel_order.pop()
        stepsize = 1

        # visit the discretized lsystem positions
        while self.reversed_pixel_order:
            x = pos[0]
            y = pos[1]
            dir = pos[2]

            brightness = qGray(image.pixel(x, y))
            if self.invertColors:
                brightness = 255 - brightness

            # handle the chosen method
            if self.minBrightness <= brightness <= self.maxBrightness:
                stepsize = methodhandler.step(x, y, dir, brightness)
            else:
                stepsize = methodhandler.skip(x, y, dir, brightness)

            # skip forward to next x,y coordinate
            for i in range(stepsize):
                if self.reversed_pixel_order:
                    pos = self.reversed_pixel_order.pop()

        group = methodhandler.finish()
        self.addNewGraphicsItems(group)

    def parse_rules(self, rules):
        result = {}
        # strip whitespace
        rules = re.sub(r'\s+', '', rules)
        # split on ;
        rules = rules.split(";")
        for r in rules:
            # split on =
            splitrule = r.split("=")
            try:
                lhs = splitrule[0]
                rhs = splitrule[1]
                result[lhs] = rhs
            except:
                pass
        return result

    def parse_constants(self, constants):
        result = set()
        # strip whitespace
        constants = re.sub(r'\s+', '', constants)
        # split on ;
        constants = constants.split(";")
        for c in constants:
            result.add(c)
        return result

    def getdata(self):
        rules = self.parent.rulesLSystify.text()
        self.rules = self.parse_rules(rules)
        self.axiom = self.parent.axiomLSystify.text()
        constants = self.parent.constantsLSystify.text()
        self.constants = self.parse_constants(constants)
        self.iterations = self.parent.iterationsLSystify.value()
        self.plusAngle = self.parent.plusAngleLSystify.value()
        self.minAngle = self.parent.minAngleLSystify.value()
        self.xoffs = self.parent.xOffsetLSystify.value()
        self.yoffs = self.parent.yOffsetLSystify.value()
        self.xscale = self.parent.xScaleLSystify.value()
        self.yscale = self.parent.yScaleLSystify.value()
        self.init_dir = np.matmul(rotmatrix(np.deg2rad(self.parent.initialAngleLSystify.value())),
                                  np.array([[1, ], [0, ]]))
        self.init_pos = np.array([[0, ], [0, ]])
        self.strokeWidth = self.parent.lineWidthLSystify.value()
        self.minBrightness = self.parent.minBrightnessLSystify.value()
        self.maxBrightness = self.parent.maxBrightnessLSystify.value()
        self.minRadius = self.parent.minRadiusLSystify.value()
        self.maxRadius = self.parent.maxRadiusLSystify.value()
        self.detail = self.parent.detailLSystify.value()
        self.strength = self.parent.strengthLSystify.value()
        self.minStepSize = self.parent.minStepSizeLSystify.value()
        self.maxStepSize = self.parent.maxStepSizeLSystify.value()
        self.method = self.parent.methodLSystify.currentText()
        self.invertColors = self.parent.invertColorsLSystify.checkState() == Qt.Checked
        self.clipToBitmap = self.parent.clipToBitmapLSystify.checkState() == Qt.Checked

    def OnMethod(self, text):
        if (text == "Circles"):
            self.parent.detailLSystify.setEnabled(False)
            self.parent.strengthLSystify.setEnabled(False)
            self.parent.minRadiusLSystify.setEnabled(True)
            self.parent.maxRadiusLSystify.setEnabled(True)
        elif (text == "Squiggles"):
            self.parent.detailLSystify.setEnabled(True)
            self.parent.strengthLSystify.setEnabled(True)
            self.parent.minRadiusLSystify.setEnabled(False)
            self.parent.maxRadiusLSystify.setEnabled(False)

    def run_lsystem(self):
        self.lsystem.set_axiom(self.axiom)
        self.lsystem.set_rules(self.rules)
        self.lsystem.set_constants(self.constants)
        self.lsystem.set_iterations(self.iterations)
        self.lsysteminterpreter.set_lsystem(self.lsystem)
        self.lsysteminterpreter.set_globalstate({
            "pts": [(self.init_pos, self.init_dir)],
            "x,y": self.init_pos,
            "dir": self.init_dir,
            "posstack": [],
            "dirstack": [],
        })
        self.lsysteminterpreter.add_action("A", self.add_dir)
        self.lsysteminterpreter.add_action("B", self.add_dir)
        self.lsysteminterpreter.add_action("Y", self.add_dir)
        self.lsysteminterpreter.add_action("X", self.add_dir)
        self.lsysteminterpreter.add_action("R", self.add_dir)
        self.lsysteminterpreter.add_action("L", self.add_dir)
        self.lsysteminterpreter.add_action("F", self.add_dir)
        self.lsysteminterpreter.add_action("+", self.rotate_cw)
        self.lsysteminterpreter.add_action("-", self.rotate_ccw)
        self.lsysteminterpreter.add_action("[", self.push_state)
        self.lsysteminterpreter.add_action("]", self.pop_state)
        self.lsysteminterpreter.run()

    def visualize(self):
        self.getdata()
        self.run_lsystem()

        layerId = QPersistentModelIndex(self.parent.layersList.currentIndex())
        if layerId not in self.itemsPerLayer:
            self.itemsPerLayer[layerId] = None
        if self.itemsPerLayer[layerId] is not None:
            self.parent.scene.removeItem(self.itemsPerLayer[layerId])

        group = QGraphicsItemGroup()
        path = QPainterPath()
        for idx, point in enumerate(self.lsysteminterpreter.globalstate["pts"]):
            x = point[0][0][0]
            y = point[0][1][0]
            dir = point[1]
            x = x * self.xscale + self.xoffs
            y = y * self.yscale + self.yoffs
            if idx == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        item = QGraphicsPathItem(path)
        pen = QPen()
        pen.setWidth(self.strokeWidth)
        item.setPen(pen)
        group.addToGroup(item)
        self.parent.scene.addItem(group)
        self.itemsPerLayer[layerId] = group

    def discretize_lsystem(self):
        discretized = []
        finalxy = []
        xs = []
        ys = []
        for idx, point in enumerate(self.lsysteminterpreter.globalstate["pts"]):
            x = point[0][0][0]
            y = point[0][1][0]
            dir = point[1]
            x = x * self.xscale + self.xoffs
            y = y * self.yscale + self.yoffs
            finalxy.append((int(x), int(y), dir))
            if idx > 0:
                # line uses bresenham's algorithm to convert the theoretical lsystem positions into pixel positions
                xs, ys = line(finalxy[-2][0], finalxy[-2][1], finalxy[-1][0], finalxy[-1][1])
                for ptindex, (x, y) in enumerate(zip(xs, ys)):
                    # never include last point
                    if ptindex < len(xs) - 1:
                        discretized.append((x, y, dir))
        # add final point, if any
        if len(xs):
            discretized.append((xs[-1], ys[-1], dir))
        return discretized
