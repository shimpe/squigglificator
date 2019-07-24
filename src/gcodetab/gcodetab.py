from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QGraphicsPathItem, QGraphicsItemGroup, QGraphicsEllipseItem

from collections import namedtuple
from tab import Tab
from gcodetab.gcodegenerator import GCodeGenerator
from os.path import expanduser

PaperOptions = namedtuple("PaperOptions", "width, height, xmargin, ymargin")

class GcodeTab(Tab):
    def __init__(self, parent=None, itemsPerLayer=None):
        super().__init__(parent, itemsPerLayer)
        self.homeFolder = expanduser("~")

    def setupSlots(self):
        self.parent.pagePresetGcode.currentTextChanged.connect(self.OnPagePreset)
        self.OnPagePreset("A4 portrait (210mm x 270mm)")
        self.parent.offsetPresetGcode.currentTextChanged.connect(self.OnOffsetPresetGcode)
        self.OnOffsetPresetGcode("Center on page")
        self.parent.xScaleGcode.valueChanged.connect(self.OnXScaleChanged)
        self.parent.yScaleGcode.valueChanged.connect(self.OnYScaleChanged)
        self.parent.lockXYGcode.clicked.connect(self.OnLockXYScaleClicked)
        self.parent.eport2dGcode.clicked.connect(self.OnGenerateGCodeAllLayers)
        self.parent.eport2dGcodePerLayer.clicked.connect(self.OnGenerateGCodePerLayer)

    def OnXScaleChanged(self, value, skip_update_dependent=False):
        if not skip_update_dependent and self.parent.lockXYGcode.isChecked():
            self.parent.xScaleGcode.blockSignals(True)
            self.parent.yScaleGcode.blockSignals(True)
            self.parent.yScaleGcode.setValue(value)
            self.OnYScaleChanged(value, True)
            self.parent.xScaleGcode.blockSignals(False)
            self.parent.yScaleGcode.blockSignals(False)
        self.update_size_label()

    def OnYScaleChanged(self, value, skip_update_dependent=False):
        if not skip_update_dependent and self.parent.lockXYGcode.isChecked():
            self.parent.xScaleGcode.blockSignals(True)
            self.parent.yScaleGcode.blockSignals(True)
            self.parent.xScaleGcode.setValue(value)
            self.OnXScaleChanged(value, True)
            self.parent.xScaleGcode.blockSignals(False)
            self.parent.yScaleGcode.blockSignals(False)
        self.update_size_label()

    def OnLockXYScaleClicked(self, checked):
        print("checked: ", checked)
        if checked:
            self.OnYScaleChanged(self.parent.xScaleGcode.value(), True)

    def OnPagePreset(self, text):
        options = {
            "A4 portrait (210mm x 270mm)": PaperOptions(width=210, height=270, xmargin=20, ymargin=20),
            "A4 landscape (270mm x 210mm)": PaperOptions(width=270, height=210, xmargin=20, ymargin=20),
            "Letter portrait (216mm x 279mm)": PaperOptions(width=216, height=279, xmargin=20, ymargin=20),
            "Letter landscape (279mm x 216mm)": PaperOptions(width=270, height=216, xmargin=20, ymargin=20),
            "Custom": PaperOptions(width=300, height=300, xmargin=0, ymargin=0)
        }
        self.parent.pageWidthGcode.setValue(options[text].width)
        self.parent.pageHeightGcode.setValue(options[text].height)
        self.parent.xMarginGcode.setValue(options[text].xmargin)
        self.parent.yMarginGcode.setValue(options[text].ymargin)

    def OnOffsetPresetGcode(self, text):
        bmheight, bmwidth = self.update_size_label()
        pw = self.parent.pageWidthGcode.value()
        ph = self.parent.pageHeightGcode.value()
        xm = self.parent.xMarginGcode.value()
        ym = self.parent.yMarginGcode.value()
        xs = self.parent.xScaleGcode.value()
        ys = self.parent.yScaleGcode.value()

        if text == "Center on page":
            self.parent.xOffsetGcode.setValue(xs*(pw - bmwidth) / 2.0)
            self.parent.yOffsetGcode.setValue(ys*(ph - bmheight) / 2.0)
        if text == "Top left page":
            self.parent.xOffsetGcode.setValue(0)
            self.parent.yOffsetGcode.setValue(ys*(ph - bmheight))
        if text == "Top right page":
            self.parent.xOffsetGcode.setValue(xs*(pw - bmwidth))
            self.parent.yOffsetGcode.setValue(ys*(ph - bmheight))
        if text == "Bottom left page":
            self.parent.xOffsetGcode.setValue(0)
            self.parent.yOffsetGcode.setValue(0)
        if text == "Bottom right page":
            self.parent.xOffsetGcode.setValue(xs*(pw - bmwidth))
            self.parent.yOffsetGcode.setValue(0)
        if text == "Center between margins":
            self.parent.xOffsetGcode.setValue(xs*(xm + (pw - xm - xm - bmwidth) / 2.0))
            self.parent.yOffsetGcode.setValue(ys*(ym + (ph - ym - ym - bmheight) / 2.0))
        if text == "Top left margins":
            self.parent.xOffsetGcode.setValue(xs*xm)
            self.parent.yOffsetGcode.setValue(ys*(ph - bmheight - ym))
        if text == "Top right margins":
            self.parent.xOffsetGcode.setValue(xs*(pw - bmwidth - xm))
            self.parent.yOffsetGcode.setValue(ys*(ph - bmheight - ym))
        if text == "Bottom left margins":
            self.parent.xOffsetGcode.setValue(xs*xm)
            self.parent.yOffsetGcode.setValue(ys*ym)
        if text == "Bottom right margins":
            self.parent.xOffsetGcode.setValue(xs*(pw - bmwidth - xm))
            self.parent.yOffsetGcode.setValue(ys*ym)

    def update_size_label(self):
        if self.parent.bitmap:
            rawwidth = self.parent.bitmap.width()
            rawheight = self.parent.bitmap.height()
        else:
            rawwidth = 0
            rawheight = 0
        bmwidth = rawwidth* self.parent.xScaleGcode.value()
        bmheight = rawheight * self.parent.yScaleGcode.value()
        ym = self.parent.yMarginGcode.value()
        xm = self.parent.xMarginGcode.value()
        maxheight = self.parent.pageHeightGcode.value() - 2*ym
        maxwidth = self.parent.pageWidthGcode.value() - 2*xm
        warnings = []
        jointwarning = ""
        if bmheight > maxheight:
            warnings.append("too high")
        if bmwidth > maxwidth:
            warnings.append("too wide")
        if warnings:
            jointwarning = " and ".join(warnings) + " to fit within margins. Max scale = {0:.2f}".format(min(maxheight/rawheight, maxwidth/rawwidth))
        else:
            jointwarning = "fits within margins"

        self.parent.labelSizeGcode.setText("current size: {0:.2f}mm x {1:.2f}mm -> {2}".format(bmwidth, bmheight, jointwarning))
        return bmheight, bmwidth

    def OnGenerateGCodeAllLayers(self):
        newPath = QFileDialog.getSaveFileName(self.parent.centralwidget, "Export .cnc all layers",
                                              self.homeFolder,
                                              "CNC files (*.cnc)")
        if not newPath[0]:
            return

        self.OnOffsetPresetGcode(self.parent.offsetPresetGcode.currentText())
        filename = newPath[0]

        gen = GCodeGenerator(self.parent.pageHeightGcode.value(),
                             self.parent.xScaleGcode.value(),
                             self.parent.yScaleGcode.value(),
                             self.parent.xOffsetGcode.value(),
                             self.parent.yOffsetGcode.value(),
                             self.parent.homeGcode.checkState() == Qt.Checked,
                             self.parent.homeEndGcode.checkState() == Qt.Checked,
                             self.parent.penUpCmdGcode.text(),
                             self.parent.penDownCmdGcode.text(),
                             self.parent.drawingSpeedGcode.value(),
                             self.parent.penDownSpeedGcode.value())
        for layer in self.itemsPerLayer:
            for item in self.itemsPerLayer[layer].childItems():
                if not item.isVisible():
                    continue
                if item.__class__ == QGraphicsEllipseItem:
                    gen.circle(item)
                elif item.__class__ == QGraphicsPathItem:
                    gen.path(item)
                else:
                    print("boehoe - {0}".format(item.__class__))

        gen.add_statistics()
        gen.footer()
        with open(filename, "w") as f:
            f.write(gen.code)

    def OnGenerateGCodePerLayer(self):
        pass
