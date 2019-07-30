import re

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import qGray, QPainterPath, QPen
from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsItemGroup
from skimage.draw import line

from lsystifytab.circlemethod import CircleMethod
from lsystifytab.lsystem import LSystem
from lsystifytab.lsysteminterpreter import LSystemInterpreter
from lsystifytab.squigglemethod import SquiggleMethod
from tab import Tab
from tab_constants import LSYSTIFYTAB


def rotmatrix(theta):
    c, s = np.cos(theta), np.sin(theta)
    R = np.array(((c, -s), (s, c)))
    return R


class LSystifyTab(Tab):
    """
    tab to represent the lsystify wizard
    """

    def __init__(self, parent=None, layersModel=None):
        super().__init__(parent, layersModel)
        self.localBitmap = None
        self.lsystem = LSystem()
        self.lsysteminterpreter = LSystemInterpreter()

    def setupSlots(self):
        """
        make the buttons do something
        :return:
        """
        self.parent.lsystify.clicked.connect(self.process)
        self.parent.drawLSystemLSystify.clicked.connect(self.visualize)
        self.parent.methodLSystify.currentTextChanged.connect(self.OnMethod)
        self.parent.presetLSystify.currentTextChanged.connect(self.OnPreset)
        self.OnMethod("Circles")
        self.OnPreset("Hilbert")

    def get_id(self):
        return LSYSTIFYTAB

    def ui_to_model(self):
        model = {'preset'       : self.parent.presetLSystify.currentText(),
                 'iterations'   : self.parent.iterationsLSystify.value(), 'axiom': self.parent.axiomLSystify.text(),
                 'rules'        : self.parent.rulesLSystify.text(), 'constants': self.parent.constantsLSystify.text(),
                 'invertColors' : int(self.parent.invertColorsLSystify.checkState()),
                 'lineWidth'    : self.parent.lineWidthLSystify.value(),
                 'clip'         : int(self.parent.clipToBitmapLSystify.checkState()),
                 'initialAngle' : self.parent.initialAngleLSystify.value(),
                 'plusAngle'    : self.parent.plusAngleLSystify.value(),
                 'minAngle'     : self.parent.minAngleLSystify.value(),
                 'xScale'       : self.parent.xScaleLSystify.value(), 'yScale': self.parent.yScaleLSystify.value(),
                 'xOffset'      : self.parent.xOffsetLSystify.value(), 'yOffset': self.parent.yOffsetLSystify.value(),
                 'method'       : self.parent.methodLSystify.currentText(),
                 'minBrightness': self.parent.minBrightnessLSystify.value(),
                 'maxBrightness': self.parent.maxBrightnessLSystify.value(),
                 'minRadius'    : self.parent.minRadiusLSystify.value(),
                 'maxRadius'    : self.parent.maxRadiusLSystify.value(),
                 'minStepSize'  : self.parent.minStepSizeLSystify.value(),
                 'maxStepSize'  : self.parent.maxStepSizeLSystify.value(),
                 'strength'     : self.parent.strengthLSystify.value(), 'detail': self.parent.detailLSystify.value()}
        return model

    def model_to_ui(self, model):
        self.parent.presetLSystify.setCurrentText(str(model['preset']))
        self.parent.iterationsLSystify.setValue(int(model['iterations']))
        self.parent.axiomLSystify.setText(str(model['axiom']))
        self.parent.rulesLSystify.setText(str(model['rules']))
        self.parent.constantsLSystify.setText(str(model['constants']))
        self.parent.invertColorsLSystify.setCheckState(int(model['invertColors']))
        self.parent.lineWidthLSystify.setValue(int(model['lineWidth']))
        self.parent.clipToBitmapLSystify.setCheckState(int(model['clip']))
        self.parent.initialAngleLSystify.setValue(float(model['initialAngle']))
        self.parent.plusAngleLSystify.setValue(float(model['plusAngle']))
        self.parent.minAngleLSystify.setValue(float(model['minAngle']))
        self.parent.xScaleLSystify.setValue(float(model['xScale']))
        self.parent.yScaleLSystify.setValue(float(model['yScale']))
        self.parent.xOffsetLSystify.setValue(float(model['xOffset']))
        self.parent.yOffsetLSystify.setValue(float(model['yOffset']))
        self.parent.methodLSystify.setCurrentText(str(model['method']))
        self.parent.minBrightnessLSystify.setValue(int(model['minBrightness']))
        self.parent.maxBrightnessLSystify.setValue(int(model['maxBrightness']))
        self.parent.minRadiusLSystify.setValue(int(model['minRadius']))
        self.parent.maxRadiusLSystify.setValue(int(model['maxRadius']))
        self.parent.minStepSizeLSystify.setValue(int(model['minStepSize']))
        self.parent.maxStepSizeLSystify.setValue(int(model['maxStepSize']))
        self.parent.strengthLSystify.setValue(float(model['strength']))
        self.parent.detailLSystify.setValue(float(model['detail']))

    @staticmethod
    def add_dir(gs):
        """
        semantic action used in the LSystem interpreter: adds direction vector to global state
        :param gs: globalstate object
        :return: new global state
        """
        gs["x,y"] = gs["x,y"] + gs["dir"]
        gs["pts"].append((gs["x,y"], gs["dir"]))
        return gs

    def rotate_cw(self, gs):
        """
        semantic action used in the LSystem interpreter: rotates direction vector clockwise over minAngle (=ui parameter)
        :param gs: global state
        :return: new global state
        """
        R = rotmatrix(np.radians(self.minAngle))
        gs["dir"] = np.matmul(R, gs["dir"])
        return gs

    def rotate_ccw(self, gs):
        """
        semantic action used in the LSystem interpreter: rotates direction vector counterclockwise over plusAngle (=ui parameter)
        :param gs: global state
        :return: new global state
        """
        R = rotmatrix(np.radians(self.plusAngle))
        gs["dir"] = np.matmul(R, gs["dir"])
        return gs

    def OnPreset(self, text):
        """
        triggered when user selects a preset
        updates ui controls to show the preset
        :param text: combo box text
        :return:
        """
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

    @staticmethod
    def push_state(gs):
        """
        semantic action used in LSystem interpreter, to remember current state
        :param gs: global state
        :return: new global state
        """
        gs["posstack"] = gs["posstack"].append(gs["x,y"])
        gs["dirstack"] = gs["dirstack"].append(gs["dir"])

    @staticmethod
    def pop_state(gs):
        """
        semantic action used in LSystem interpreter, to go back to previous state
        :param gs: global state
        :return: new global state
        """
        if gs["posstack"]:
            gs["posstack"].pop()
        if gs["dirstack"]:
            gs["dirstack"].pop()

    def process_without_signals(self):
        """
        calculates the lsystification of bitmap, i.e. the lsystem is used as iterator through the bitmap
        :return:
        """
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

    def process(self):
        self.process_without_signals()
        self.last_used_method.emit(self.parent.layersList.currentIndex(), self.get_id())

    def make(self, image):
        """
        the actual calculations, done on successive pixel positions popped from in self.reversed_pixel_order
        self.reversed_pixel_order was initialized with a call to discretize_lsystem()

        :param image: bitmap on wich to operate
        :return:
        """
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
        else:
            assert False

        pos = self.reversed_pixel_order.pop()
        stepsize = 1

        # visit the discretized lsystem positions
        while self.reversed_pixel_order:
            x = pos[0]
            y = pos[1]
            direction = pos[2]

            brightness = qGray(image.pixel(x, y))
            if self.invertColors:
                brightness = 255 - brightness

            # handle the chosen method
            if self.minBrightness <= brightness <= self.maxBrightness:
                stepsize = methodhandler.step(x, y, direction, brightness)
            else:
                stepsize = methodhandler.skip(x, y, direction, brightness)

            # skip forward to next x,y coordinate
            for i in range(stepsize):
                if self.reversed_pixel_order:
                    pos = self.reversed_pixel_order.pop()

        group = methodhandler.finish()
        self.addNewGraphicsItems(group)

    @staticmethod
    def parse_rules(rules):
        """
        parse rules from ui specification into LSystem rules
        :param rules:
        :return:
        """
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

    @staticmethod
    def parse_constants(constants):
        """
        Parse constants from Ui into LSystem constants
        :param constants:
        :return:
        """
        result = set()
        # strip whitespace
        constants = re.sub(r'\s+', '', constants)
        # split on ;
        constants = constants.split(";")
        for c in constants:
            result.add(c)
        return result

    def getdata(self):
        """
        set up some data from ui controls (maybe this is a bit overkill? other tabs directly access self.parent...)
        :return:
        """
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
        """
        triggered if method combo box is changed
        :param text:
        :return:
        """
        if text == "Circles":
            self.parent.detailLSystify.setEnabled(False)
            self.parent.strengthLSystify.setEnabled(False)
            self.parent.minRadiusLSystify.setEnabled(True)
            self.parent.maxRadiusLSystify.setEnabled(True)
        elif text == "Squiggles":
            self.parent.detailLSystify.setEnabled(True)
            self.parent.strengthLSystify.setEnabled(True)
            self.parent.minRadiusLSystify.setEnabled(False)
            self.parent.maxRadiusLSystify.setEnabled(False)

    def run_lsystem(self):
        """
        interpret the lsystem defined by the user
        :return:
        """
        self.lsystem.set_axiom(self.axiom)
        self.lsystem.set_rules(self.rules)
        self.lsystem.set_constants(self.constants)
        self.lsystem.set_iterations(self.iterations)
        self.lsysteminterpreter.set_lsystem(self.lsystem)
        self.lsysteminterpreter.set_globalstate({
            "pts"     : [(self.init_pos, self.init_dir)],
            "x,y"     : self.init_pos,
            "dir"     : self.init_dir,
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
        """
        called when user clicks draw lsystem. This visualizes the lsystem to allow setup
        before the actual lsystification takes place
        """
        self.getdata()
        self.run_lsystem()

        old_group = self.layersModel.itemFromIndex(self.parent.layersList.currentIndex()).get_graphics_items_group()
        if old_group:
            self.parent.scene.removeItem(old_group)

        group = QGraphicsItemGroup()
        path = QPainterPath()
        for idx, point in enumerate(self.lsysteminterpreter.globalstate["pts"]):
            x = point[0][0][0]
            y = point[0][1][0]
            direction = point[1]
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
        self.addNewGraphicsItems(group)

    def discretize_lsystem(self):
        """
        this method converts the lsystem (taking into account scaling factors) into concrete bitmap x,y positions to visit
        :return:
        """
        discretized = []
        finalxy = []
        xs = []
        ys = []
        direction = np.array([[0, ], [1, ]])
        for idx, point in enumerate(self.lsysteminterpreter.globalstate["pts"]):
            x = point[0][0][0]
            y = point[0][1][0]
            direction = point[1]
            x = x * self.xscale + self.xoffs
            y = y * self.yscale + self.yoffs
            finalxy.append((int(x), int(y), direction))
            if idx > 0:
                # line uses bresenham's algorithm to convert the theoretical lsystem positions into pixel positions
                xs, ys = line(finalxy[-2][0], finalxy[-2][1], finalxy[-1][0], finalxy[-1][1])
                for ptindex, (x, y) in enumerate(zip(xs, ys)):
                    # never include last point
                    if ptindex < len(xs) - 1:
                        discretized.append((x, y, direction))
        # add final point, if any
        if len(xs):
            discretized.append((xs[-1], ys[-1], direction))
        return discretized
