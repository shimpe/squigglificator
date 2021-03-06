from collections import namedtuple
from os.path import expanduser, splitext

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QGraphicsPixmapItem, QGraphicsItemGroup

from gcodetab.gcodegenerator import GCodeGenerator
from tab import Tab
from tab_constants import GCODETAB

PaperOptions = namedtuple("PaperOptions", "width, height, xmargin, ymargin")


class GcodeTab(Tab):
    """
    gcode generation tab
    """

    def __init__(self, parent=None, layersModel=None):
        super().__init__(parent, layersModel)
        self.homeFolder = expanduser("~")

    def setupSlots(self):
        """
        set up slots for different buttons and combo boxes
        :return:
        """
        self.parent.pagePresetGcode.currentTextChanged.connect(self.OnPagePreset)
        self.OnPagePreset("A4 portrait (210mm x 270mm)")
        self.parent.offsetPresetGcode.currentTextChanged.connect(self.OnOffsetPresetGcode)
        self.OnOffsetPresetGcode("Center on page")
        self.parent.xScaleGcode.valueChanged.connect(self.OnXScaleChanged)
        self.parent.yScaleGcode.valueChanged.connect(self.OnYScaleChanged)
        self.parent.lockXYGcode.clicked.connect(self.OnLockXYScaleClicked)
        self.parent.eport2dGcode.clicked.connect(self.OnGenerateGCodeAllLayers)
        self.parent.eport2dGcodePerLayer.clicked.connect(self.OnGenerateGCodePerLayer)

    @staticmethod
    def get_id():
        return GCODETAB

    def ui_to_model(self):
        model = {'pagePreset'        : self.parent.pagePresetGcode.currentText(),
                 'pageWidth'         : self.parent.pageWidthGcode.value(),
                 'pageHeight'        : self.parent.pageHeightGcode.value(),
                 'xMargin'           : self.parent.xMarginGcode.value(), 'yMargin': self.parent.yMarginGcode.value(),
                 'xScale'            : self.parent.xScaleGcode.value(), 'yScale': self.parent.yScaleGcode.value(),
                 'lockXY'            : self.parent.lockXYGcode.isChecked(),
                 'offsetPreset'      : self.parent.offsetPresetGcode.currentText(),
                 'xOffset'           : self.parent.xOffsetGcode.value(), 'yOffset': self.parent.yOffsetGcode.value(),
                 'penUp'             : self.parent.penUpCmdGcode.text(), 'penDown': self.parent.penDownCmdGcode.text(),
                 'drawingSpeed'      : self.parent.drawingSpeedGcode.value(),
                 'penDownSpeed'      : self.parent.penDownSpeedGcode.value(),
                 'samplingDistance'  : self.parent.samplingDistanceGcode.value(),
                 'approximationError': self.parent.maximumApproximationErrorGcode.value(),
                 'homeBegin'         : int(self.parent.homeGcode.checkState()),
                 'homeEdnd'          : int(self.parent.homeEndGcode.checkState())}
        return model

    def model_to_ui(self, model):
        self.parent.pagePresetGcode.setCurrentText(str(model['pagePreset']))
        self.parent.pageWidthGcode.setValue(int(model['pageWidth']))
        self.parent.pageHeightGcode.setValue(int(model['pageHeight']))
        self.parent.xMarginGcode.setValue(int(model['xMargin']))
        self.parent.yMarginGcode.setValue(int(model['yMargin']))
        self.parent.xScaleGcode.setValue(float(model['xScale']))
        self.parent.yScaleGcode.setValue(float(model['yScale']))
        self.parent.lockXYGcode.setChecked(bool(model['lockXY']))
        self.parent.offsetPresetGcode.setCurrentText(str(model['offsetPreset']))
        self.parent.xOffsetGcode.setValue(float(model['xOffset']))
        self.parent.yOffsetGcode.setValue(float(model['yOffset']))
        self.parent.penUpCmdGcode.setText(str(model['penUp']))
        self.parent.penDownCmdGcode.setText(str(model['penDown']))
        self.parent.drawingSpeedGcode.setValue(int(model['drawingSpeed']))
        self.parent.penDownSpeedGcode.setValue(int(model['penDownSpeed']))
        self.parent.samplingDistanceGcode.setValue(float(model['samplingDistance']))
        self.parent.maximumApproximationErrorGcode.setValue(float(model['approximationError']))
        self.parent.homeGcode.setCheckState(int(model['homeBegin']))
        self.parent.homeEndGcode.setCheckState(int(model['homeEdnd']))

    def after_load_bitmap(self):
        """
        triggered by mainwindow after user loaded a bitmap
        :return:
        """
        self.OnOffsetPresetGcode(self.parent.offsetPresetGcode.currentText())
        self.update_size_label()

    def OnXScaleChanged(self, value, skip_update_dependent=False):
        """
        triggered if xscale changed: used to update margin check message
        :param value:
        :param skip_update_dependent: cludge to avoid signal/slot infinite loop
        :return:
        """
        if not skip_update_dependent and self.parent.lockXYGcode.isChecked():
            self.parent.xScaleGcode.blockSignals(True)
            self.parent.yScaleGcode.blockSignals(True)
            self.parent.yScaleGcode.setValue(value)
            self.OnYScaleChanged(value, True)
            self.parent.xScaleGcode.blockSignals(False)
            self.parent.yScaleGcode.blockSignals(False)
        self.OnOffsetPresetGcode(self.parent.offsetPresetGcode.currentText())
        self.update_size_label()

    def OnYScaleChanged(self, value, skip_update_dependent=False):
        """
        triggered if yscale changed: used to update margin check message
        :param value:
        :param skip_update_dependent: cludge to avoid signal/slot infinite loop
        :return:
        """
        if not skip_update_dependent and self.parent.lockXYGcode.isChecked():
            self.parent.xScaleGcode.blockSignals(True)
            self.parent.yScaleGcode.blockSignals(True)
            self.parent.xScaleGcode.setValue(value)
            self.OnXScaleChanged(value, True)
            self.parent.xScaleGcode.blockSignals(False)
            self.parent.yScaleGcode.blockSignals(False)
        self.OnOffsetPresetGcode(self.parent.offsetPresetGcode.currentText())
        self.update_size_label()

    def OnLockXYScaleClicked(self, checked):
        """
        triggered if user checks/unchecks lock xy scale button: used to maintain consistency between x/y scale
        :param checked:
        :return:
        """
        print("checked: ", checked)
        if checked:
            self.OnYScaleChanged(self.parent.xScaleGcode.value(), True)

    def OnPagePreset(self, text):
        """
        triggered when user defines page size
        :param text: selected page preset combobox text
        :return:
        """
        options = {
            "A4 portrait (210mm x 270mm)"     : PaperOptions(width=210, height=270, xmargin=20, ymargin=20),
            "A4 landscape (270mm x 210mm)"    : PaperOptions(width=270, height=210, xmargin=20, ymargin=20),
            "Letter portrait (216mm x 279mm)" : PaperOptions(width=216, height=279, xmargin=20, ymargin=20),
            "Letter landscape (279mm x 216mm)": PaperOptions(width=270, height=216, xmargin=20, ymargin=20),
            "Custom"                          : PaperOptions(width=300, height=300, xmargin=0, ymargin=0)
        }
        self.parent.pageWidthGcode.setValue(options[text].width)
        self.parent.pageHeightGcode.setValue(options[text].height)
        self.parent.xMarginGcode.setValue(options[text].xmargin)
        self.parent.yMarginGcode.setValue(options[text].ymargin)
        self.OnOffsetPresetGcode(self.parent.offsetPresetGcode.currentText())
        self.update_size_label()

    def OnOffsetPresetGcode(self, text):
        """
        triggered to recalculate offsets to correctly position drawing on page
        :param text: selected offset preset combobox text
        :return:
        """
        bmheight, bmwidth, warnings = self.update_size_label()
        pw = self.parent.pageWidthGcode.value()
        ph = self.parent.pageHeightGcode.value()
        xm = self.parent.xMarginGcode.value()
        ym = self.parent.yMarginGcode.value()

        if text == "Center on page":
            self.parent.xOffsetGcode.setValue((pw - bmwidth) / 2.0)
            self.parent.yOffsetGcode.setValue((ph - bmheight) / 2.0)
        if text == "Top left page":
            self.parent.xOffsetGcode.setValue(0)
            self.parent.yOffsetGcode.setValue((ph - bmheight))
        if text == "Top right page":
            self.parent.xOffsetGcode.setValue((pw - bmwidth))
            self.parent.yOffsetGcode.setValue((ph - bmheight))
        if text == "Bottom left page":
            self.parent.xOffsetGcode.setValue(0)
            self.parent.yOffsetGcode.setValue(0)
        if text == "Bottom right page":
            self.parent.xOffsetGcode.setValue((pw - bmwidth))
            self.parent.yOffsetGcode.setValue(0)
        if text == "Center between margins":
            self.parent.xOffsetGcode.setValue((xm + (pw - xm - xm - bmwidth) / 2.0))
            self.parent.yOffsetGcode.setValue((ym + (ph - ym - ym - bmheight) / 2.0))
        if text == "Top left margins":
            self.parent.xOffsetGcode.setValue(xm)
            self.parent.yOffsetGcode.setValue((ph - bmheight - ym))
        if text == "Top right margins":
            self.parent.xOffsetGcode.setValue((pw - bmwidth - xm))
            self.parent.yOffsetGcode.setValue((ph - bmheight - ym))
        if text == "Bottom left margins":
            self.parent.xOffsetGcode.setValue(xm)
            self.parent.yOffsetGcode.setValue(ym)
        if text == "Bottom right margins":
            self.parent.xOffsetGcode.setValue((pw - bmwidth - xm))
            self.parent.yOffsetGcode.setValue(ym)

    def update_size_label(self):
        """
        method to check if drawing fits between margins
        for now only bitmap dimensions are checked
        :return: scaled bitmap with, scaled bitmap height, list of warnings
        """
        if self.parent.bitmap:
            rawwidth = self.parent.bitmap.width()
            rawheight = self.parent.bitmap.height()
        else:
            rawwidth = 0
            rawheight = 0
        bmwidth = rawwidth * self.parent.xScaleGcode.value()
        bmheight = rawheight * self.parent.yScaleGcode.value()
        ym = self.parent.yMarginGcode.value()
        xm = self.parent.xMarginGcode.value()
        maxheight = self.parent.pageHeightGcode.value() - 2 * ym
        maxwidth = self.parent.pageWidthGcode.value() - 2 * xm
        warnings = []
        jointwarning = ""
        if bmheight > maxheight:
            warnings.append("too high")
        if bmwidth > maxwidth:
            warnings.append("too wide")
        if warnings:
            jointwarning = " and ".join(warnings) + " to fit within margins. Max scale = {0:.2f}".format(
                min(maxheight / rawheight, maxwidth / rawwidth))
        else:
            jointwarning = "fits within margins"

        self.parent.labelSizeGcode.setText(
            "current size: {0:.2f}mm x {1:.2f}mm -> {2}".format(bmwidth, bmheight, jointwarning))
        return bmheight, bmwidth, warnings

    def OnGenerateGCodeAllLayers(self):
        """
        triggered if user clicks generate 2d gcode all layers button in ui
        :return:
        """
        newPath = QFileDialog.getSaveFileName(self.parent.centralwidget, "Export .cnc all layers",
                                              self.homeFolder,
                                              "CNC files (*.cnc)")
        if not newPath[0]:
            return

        self.OnOffsetPresetGcode(self.parent.offsetPresetGcode.currentText())
        filename = newPath[0]

        gen = self.generate_code()
        with open(filename, "w") as f:
            f.write(gen.code)

    def OnGenerateGCodePerLayer(self):
        """
        triggered if user clicks generate 2d gcode per layer layers button in ui
        :return:
        """
        newPath = QFileDialog.getSaveFileName(self.parent.centralwidget, "Export .cnc per layer",
                                              self.homeFolder,
                                              "CNC files (*.cnc)")
        if not newPath[0]:
            return

        filename = newPath[0]

        # make stuff invisible to avoid sending it to gcode
        for layer_idx in range(self.layersModel.rowCount()):
            print("*** iteration {0}".format(layer_idx))
            layer_filename = "{0}_layer{1}.cnc".format(splitext(filename)[0], layer_idx + 1)
            for item in self.parent.scene.items():
                item.setVisible(True)
                forceAlwaysInvisible = item.__class__ == QGraphicsPixmapItem
                forceInvisibleInCurrentLayer = item.__class__ == QGraphicsItemGroup and \
                                               (item != self.layersModel.item(layer_idx).get_graphics_items_group() or \
                                                self.parent.layersModel.item(layer_idx).checkState() != Qt.Checked)
                if forceAlwaysInvisible or forceInvisibleInCurrentLayer:  # ouch
                    print("setting idx to invisible for item {0}".format(item))
                    item.setVisible(False)
            if self.parent.layersModel.item(layer_idx).checkState() == Qt.Checked:
                gen = self.generate_code()
                with open(layer_filename, "w") as f:
                    f.write(gen.code)

        # restore visibility
        for layer_idx in range(self.layersModel.rowCount()):
            for item in self.parent.scene.items():
                if item.__class__ == QGraphicsItemGroup and \
                        self.parent.layersModel.item(layer_idx).checkState() == Qt.Checked:  # ouch
                    item.setVisible(True)

    def generate_code(self):
        """
        method that runs over items in the graphics scene and generates gcode from it
        :return:
        """
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
                             self.parent.penDownSpeedGcode.value(),
                             self.parent.samplingDistanceGcode.value(),
                             self.parent.maximumApproximationErrorGcode.value())
        for layer_idx in range(self.layersModel.rowCount()):
            for item in self.layersModel.item(layer_idx).get_graphics_items_group().childItems():
                gen.process_item(item)
        gen.add_statistics()
        gen.footer()
        return gen

    def get_sketch_code(self):
        """
        method called from different tab to get gcode for all layers
        :return:
        """
        self.OnOffsetPresetGcode(self.parent.offsetPresetGcode.currentText())
        return self.generate_code()

    def get_sketch_by_layer(self):
        """
        method called from different tab to get a list of gcode per layer
        :return:
        """
        # make stuff invisible to avoid sending it to gcode
        list_of_gen = []
        for layer_idx in range(self.layersModel.rowCount()):
            for item in self.parent.scene.items():
                item.setVisible(True)
                forceAlwaysInvisible = item.__class__ == QGraphicsPixmapItem
                forceInvisibleInCurrentLayer = item.__class__ == QGraphicsItemGroup and \
                                               (item != self.layersModel.item(layer_idx).get_graphics_items_group() or \
                                                self.parent.layersModel.item(layer_idx).checkState() != Qt.Checked)
                if forceAlwaysInvisible or forceInvisibleInCurrentLayer:  # ouch
                    item.setVisible(False)
            if self.parent.layersModel.item(layer_idx).checkState() == Qt.Checked:
                list_of_gen.append(self.generate_code())

        # restore visibility
        for layer_idx in range(self.layersModel.rowCount()):
            for item in self.parent.scene.items():
                if item.__class__ == QGraphicsItemGroup and \
                        self.parent.layersModel.item(layer_idx).checkState() == Qt.Checked:  # ouch
                    item.setVisible(True)

        return list_of_gen

    def check_drawing_fits(self):
        """
        method called from different tab to check if drawing fits between margins
        :return:
        """
        bmwidth, bmheight, warnings = self.update_size_label()
        return warnings
