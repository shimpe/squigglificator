import os
from os.path import expanduser

import yaml
from PyQt5.QtCore import Qt, QPersistentModelIndex, QModelIndex, QRect
from PyQt5.QtGui import QImage, QPixmap, QStandardItemModel, QPainter
from PyQt5.QtSvg import QSvgGenerator
from PyQt5.QtWidgets import QFileDialog, QGraphicsScene, QGraphicsPixmapItem, QGraphicsItemGroup, QMessageBox

from bubblifytab.bubblifytab import BubblifyTab
from gcodesendertab.gcodesendertab import GcodeSenderTab
from gcodetab.gcodetab import GcodeTab
from img2svg import Ui_MainWindow
from layeritem import LayerItem
from lsystifytab.lsystifytab import LSystifyTab
from squigglifytab.squigglifytab import SquigglifyTab

TABS_WITH_PER_LAYER_PARAMS = [SquigglifyTab, BubblifyTab, LSystifyTab]
TABS_OVER_ALL_LAYERS = [GcodeTab, GcodeSenderTab]


class MyMainWindow(Ui_MainWindow):
    """
    main window class
    """

    def __init__(self, application):
        super().__init__()
        self.application = application
        self.homeFolder = expanduser("~")
        self.properties_over_all_layers_per_tab = {}

    def finishSetupUi(self):
        """
        initialize models, tabs
        :return: nothing
        """
        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.bitmap = None
        self.bitmapItem = None
        self.previousPath = None
        self.homeFolder = None
        self.layersModel = QStandardItemModel()
        self.layersList.setModel(self.layersModel)
        self.previousActiveLayer = None
        self.itemsPerLayer = {}
        self.tabs = [SquigglifyTab, BubblifyTab, LSystifyTab, GcodeTab, GcodeSenderTab]
        self.tabhandlers = [t(self, self.itemsPerLayer) for t in self.tabs]
        self.AddLayer()
        self.layersList.setCurrentIndex(self.layersModel.index(0, 0))
        self.bitmapVisibility = True
        self.generated = {}

    def setupSlots(self):
        """
        called to set up mainwindow and tab slots
        :return:
        """
        self.loadBitmap.clicked.connect(self.LoadBitmap)
        self.hideBitmap.clicked.connect(self.ToggleBitmap)
        self.actionZoom_In.triggered.connect(self.ActionZoom_In)
        self.actionZoom_to.triggered.connect(self.ActionZoom_to)
        self.actionZoom_Out.triggered.connect(self.ActionZoom_Out)

        self.actionLoad_Bitmap.triggered.connect(self.LoadBitmap)
        self.actionExport_SVG.triggered.connect(self.ExportSVG)
        self.actionShow_toolbar.triggered.connect(self.ShowToolbar)
        self.actionQuit.triggered.connect(self.OnQuit)
        self.actionQuit_2.triggered.connect(self.OnQuit)
        self.actionShow_layers.triggered.connect(self.ShowLayers)
        self.actionExport_SVG_one_file_per_layer.triggered.connect(self.ExportSVGPerLayer)

        self.application.aboutToQuit.connect(self.OnQuit)

        self.addLayer.clicked.connect(self.AddLayer)
        self.removeLayer.clicked.connect(self.RemoveSelected)
        self.layersModel.itemChanged.connect(self.LayerChanged)
        self.layersList.clicked.connect(self.LayerSelectionChanged)
        self.exportSvg.clicked.connect(self.ExportSVG)
        self.exportSvgPerLayer.clicked.connect(self.ExportSVGPerLayer)
        for t in self.tabhandlers:
            t.setupSlots()
            t.last_used_method.connect(self.UpdateLastUsedMethod)

        self.saveSketch.clicked.connect(self.SaveSketch)
        self.loadSketch.clicked.connect(self.LoadSketch)

    def LoadSketch(self):
        fname = QFileDialog.getOpenFileName(self.centralwidget, 'Open sketch',
                                            self.homeFolder, "Sketch files (*.sq)")[0]
        if not fname:
            return

        with open(fname, 'r') as stream:
            try:
                simple_model = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                QMessageBox.error("Problem loading .sq file!! Reason: {0}".format(exc))
                return

        self.layersModel.clear()
        for layer in self.itemsPerLayer:
            if self.itemsPerLayer[layer] is not None:
                self.scene.removeItem(self.itemsPerLayer[layer])
        self.properties_over_all_layers_per_tab = {}
        no_of_layers = len(simple_model["layer_dependent_parameters"].keys())
        for l in range(no_of_layers):
            self.AddLayer()
            for tab in TABS_WITH_PER_LAYER_PARAMS:
                tabidx = tab().get_id()
                self.layersModel.item(l, 0).set_parameters_for_tab(tabidx,
                                                                   simple_model["layer_dependent_parameters"][l][
                                                                       tabidx])
                self.layersModel.item(l, 0).set_last_used_method(
                    simple_model["layer_dependent_parameters"][l]["last_used_method"])
        self.properties_over_all_layers_per_tab = simple_model["layer_independent_parameters"]

    def SaveSketch(self):
        fname = QFileDialog.getSaveFileName(self.centralwidget, 'Save sketch',
                                            self.homeFolder, "Sketch files (*.sq)")[0]
        if not fname:
            return

        summary_model = {}
        summary_model["layer_independent_parameters"] = self.properties_over_all_layers_per_tab
        summary_model["layer_dependent_parameters"] = {}
        for l in range(self.layersModel.rowCount()):
            data = self.layersModel.item(l, 0).get_parameters()
            summary_model["layer_dependent_parameters"][l] = data
            last_used_method = self.layersModel.item(l, 0).get_last_used_method()
            summary_model["layer_dependent_parameters"][l]["last_used_method"] = last_used_method
        with open(fname, 'w') as outfile:
            yaml.dump(summary_model, outfile, default_flow_style=False)

    def UpdateLastUsedMethod(self, layer_model_index, method):
        self.layersModel.itemFromIndex(QModelIndex(layer_model_index)).set_last_used_method(method)

    def ShowToolbar(self):
        """
        action triggered when user requests to see buttons toolbar
        :return:
        """
        self.toolBar.setVisible(True)

    def ShowLayers(self):
        """
        action triggered when user requests to see layers toolbar
        :return:
        """
        self.layers.setVisible(True)

    def OnQuit(self):
        """
        action triggered when the application is about to quit -> give each tab a chance to clean up after itself
        :return:
        """
        for t in self.tabhandlers:
            t.on_quit()
        import sys
        sys.exit()

    def LoadBitmap(self):
        """
        action triggered when the user requests to load a bitmap
        :return:
        """
        fname = QFileDialog.getOpenFileName(self.centralwidget, 'Open file',
                                            self.homeFolder, "Image files (*.jpg *.jpeg *.gif *.png *.bmp)")[0]
        if fname:
            # clean up all old data
            for layer in self.itemsPerLayer:
                if self.itemsPerLayer[layer] is not None:
                    self.scene.removeItem(self.itemsPerLayer[layer])
            # create new data
            self.bitmap = QImage(fname)
            if self.bitmap:
                if self.bitmapItem is not None:
                    self.scene.removeItem(self.bitmapItem)
                self.bitmapItem = QGraphicsPixmapItem(QPixmap.fromImage(self.bitmap))
                self.scene.addItem(self.bitmapItem)
                self.hideBitmap.setText("Hide Bitmap")
                self.bitmapVisibility = True

        for t in self.tabhandlers:
            t.after_load_bitmap()

    def ActionZoom_In(self):
        """
        action triggered when user requests zooming in using mousewheel
        :return:
        """
        # Zoom Factor
        zoomInFactor = 1.25
        self.graphicsView.scale(zoomInFactor, zoomInFactor)

    def ActionZoom_Out(self):
        """
        action triggered when user requests zooming out using mousewheel
        :return:
        """
        # Zoom Factor
        zoomInFactor = 1 / 1.25
        self.graphicsView.scale(zoomInFactor, zoomInFactor)

    def ActionZoom_to(self):
        """
        action triggered when user requests zoom to fit
        :return:
        """
        self.graphicsView.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def AddLayer(self):
        """
        action triggered when user requests addition of a new layer
        :return:
        """
        item = LayerItem("Layer {0}".format(self.layersModel.rowCount() + 1))
        params_per_tab = {}
        for tab in TABS_WITH_PER_LAYER_PARAMS:
            tabidx = tab().get_id()
            item.set_parameters_for_tab(tabidx, self.tabhandlers[tabidx].ui_to_model())
        for tab in TABS_OVER_ALL_LAYERS:
            tabidx = tab().get_id()
            self.properties_over_all_layers_per_tab[tabidx] = self.tabhandlers[tabidx].ui_to_model()
        self.layersModel.appendRow(item)

    def RemoveSelected(self):
        """
        action triggered when user requests removal of selected layer
        :return:
        """
        for i in self.layersList.selectedIndexes():
            index = QPersistentModelIndex(i)
            if index in self.itemsPerLayer:
                self.scene.removeItem(self.itemsPerLayer[index])
                del self.itemsPerLayer[index]
            self.layersModel.removeRow(i.row())
        if self.layersModel.rowCount() == 0:
            self.AddLayer()
            self.layersList.setCurrentIndex(self.layersModel.index(0, 0))

    def ToggleBitmap(self):
        """
        action triggered when user requests to hide/show bitmap
        :return:
        """
        if self.bitmapVisibility:
            if self.bitmapItem:
                self.scene.removeItem(self.bitmapItem)
            self.hideBitmap.setText("Show Bitmap")
            self.bitmapVisibility = False
        else:
            if self.bitmapItem:
                self.bitmapItem.setZValue(-1)
                self.scene.addItem(self.bitmapItem)
            self.hideBitmap.setText("Hide Bitmap")
            self.bitmapVisibility = True

    def LayerSelectionChanged(self, new_layer):
        persistent_new_layer = QPersistentModelIndex(new_layer)
        if self.previousActiveLayer is None:
            previous_layer = QPersistentModelIndex(self.layersModel.index(0, 0))
        else:
            previous_layer = self.previousActiveLayer
        self.previousActiveLayer = persistent_new_layer

        # remember parameter settings from previous layer when switching to new layer
        # store layer dependent parameters
        if previous_layer.isValid():  # could have been deleted...
            for t in TABS_WITH_PER_LAYER_PARAMS:
                tabidx = t().get_id()
                self.layersModel.itemFromIndex(QModelIndex(previous_layer)).parameters_per_tab[tabidx] = \
                    self.tabhandlers[tabidx].ui_to_model()

        # store overall parameters
        for t in TABS_OVER_ALL_LAYERS:
            tabidx = t().get_id()
            self.properties_over_all_layers_per_tab[tabidx] = self.tabhandlers[tabidx].ui_to_model()

        # show parameter settings on newly selected layer if they were stored in a previous visit already
        for t in TABS_WITH_PER_LAYER_PARAMS:
            tabidx = t().get_id()
            self.tabhandlers[tabidx].model_to_ui(
                self.layersModel.itemFromIndex(new_layer).get_parameters_for_tab(tabidx))

        # restore overall parameters
        for t in TABS_OVER_ALL_LAYERS:
            tabidx = t().get_id()
            if tabidx in self.properties_over_all_layers_per_tab:
                self.tabhandlers[tabidx].model_to_ui(self.properties_over_all_layers_per_tab[tabidx])

        # also make last used method the active tab
        last_used_method = self.layersModel.itemFromIndex(new_layer).get_last_used_method()
        self.squigglifySetup.setCurrentIndex(last_used_method)

    def LayerChanged(self):
        """
        action triggered when user checks/unchecks a layer
        :return:
        """
        numRows = self.layersModel.rowCount()
        for row in range(numRows):
            item = self.layersModel.item(row)
            index = QPersistentModelIndex(self.layersModel.index(row, 0))
            if index not in self.itemsPerLayer:
                return
            if item.checkState() == Qt.Checked:
                self.itemsPerLayer[index].setVisible(True)
            else:
                self.itemsPerLayer[index].setVisible(False)

    def ExportSVG(self):
        """
        action triggered when user exports current graphics as svg
        :return:
        """
        newPath = QFileDialog.getSaveFileName(self.centralwidget, "Export .svg",
                                              self.homeFolder,
                                              "SVG files (*.svg)")
        if not newPath[0]:
            return

        filename = newPath[0]
        if self.bitmapVisibility:
            self.ToggleBitmap()
        generator = QSvgGenerator()
        generator.setFileName(filename)
        sceneSize = self.scene.sceneRect().size()
        generator.setSize(sceneSize.toSize())
        generator.setViewBox(QRect(0, 0, sceneSize.width(), sceneSize.height()))
        generator.setDescription("generated by SVG generator")
        generator.setTitle(filename)
        painter = QPainter()
        painter.begin(generator)
        self.scene.render(painter)
        painter.end()

    def ExportSVGPerLayer(self):
        """
        action triggered when user exports current graphics as one svg per layer
        :return:
        """
        newPath = QFileDialog.getSaveFileName(self.centralwidget, "Export .svg per layer",
                                              self.homeFolder,
                                              "SVG files (*.svg)")
        if not newPath[0]:
            return

        filename = newPath[0]

        if self.bitmapVisibility:
            self.ToggleBitmap()

        # make stuff invisible to avoid sending it to svg
        for idx, layer in enumerate(self.itemsPerLayer):
            print("*** iteration {0}".format(idx))
            layer_filename = "{0}_layer{1}.svg".format(os.path.splitext(filename)[0], idx + 1)
            for item in self.scene.items():
                item.setVisible(True)
                forceAlwaysInvisible = item.__class__ == QGraphicsPixmapItem
                forceInvisibleInCurrentLayer = item.__class__ == QGraphicsItemGroup and \
                                               (item != self.itemsPerLayer[layer] or \
                                                self.layersModel.item(idx).checkState() != Qt.Checked)
                if forceAlwaysInvisible or forceInvisibleInCurrentLayer:  # ouch
                    print("setting idx to invisible for item {0}".format(item))
                    item.setVisible(False)
            if self.layersModel.item(idx).checkState() == Qt.Checked:
                generator = QSvgGenerator()
                generator.setFileName(layer_filename)
                sceneSize = self.scene.sceneRect().size()
                generator.setSize(sceneSize.toSize())
                generator.setViewBox(QRect(0, 0, sceneSize.width(), sceneSize.height()))
                generator.setDescription("generated by SVG generator")
                generator.setTitle(layer_filename)
                painter = QPainter()
                painter.begin(generator)
                self.scene.render(painter)
                painter.end()

        # restore visibility
        for idx, layer in enumerate(self.itemsPerLayer):
            for item in self.scene.items():
                if item.__class__ == QGraphicsItemGroup and \
                        self.layersModel.item(idx).checkState() == Qt.Checked:  # ouch
                    item.setVisible(True)

    def get_sketch_code(self):
        """
        method used to be able to call code generation (implemented in gcodetab) from gcodesendertab
        :return: an object containing gcode
        """
        tabidx = self.tabs.index(GcodeTab)
        return self.tabhandlers[tabidx].get_sketch_code()

    def get_sketch_by_layer(self):
        """
        method used to be able to call code generation (implemented in gcodetab) from gcodesendertab
        :return: a list of objects containing gcode
        """
        tabidx = self.tabs.index(GcodeTab)
        return self.tabhandlers[tabidx].get_sketch_by_layer()

    def check_drawing_fits(self):
        """
        method used to check that drawing fits within margins (implemented in gcodetab) from gcodesendertab
        :return: boolean
        """
        tabidx = self.tabs.index(GcodeTab)
        return self.tabhandlers[tabidx].check_drawing_fits()
