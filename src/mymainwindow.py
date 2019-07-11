import os
from img2svg import Ui_MainWindow
from PyQt5.QtWidgets import QFileDialog, QGraphicsScene, QGraphicsPixmapItem, QGraphicsItemGroup
from PyQt5.QtGui import QImage, QPixmap, QStandardItemModel, QStandardItem, QBrush, QPainter
from PyQt5.QtCore import Qt, QModelIndex, QPersistentModelIndex, QRect, QRectF
from PyQt5.QtSvg import QSvgGenerator
from squigglifytab import SquigglifyTab


class MyMainWindow(Ui_MainWindow):

    def __init__(self):
        super().__init__()

    def finishSetupUi(self):
        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.bitmap = None
        self.bitmapItem = None
        self.previousPath = None
        self.homeFolder = None
        self.layersModel = QStandardItemModel()
        self.layersList.setModel(self.layersModel)
        self.AddLayer()
        self.layersList.setCurrentIndex(self.layersModel.index(0, 0))
        self.bitmapVisibility = True
        self.generated = {}
        self.itemsPerLayer = {}
        self.squigglifyTabHandler = SquigglifyTab(self, self.itemsPerLayer)

    def setupSlots(self):
        self.loadBitmap.clicked.connect(self.LoadBitmap)
        self.hideBitmap.clicked.connect(self.ToggleBitmap)
        self.actionZoom_In.triggered.connect(self.ActionZoom_In)
        self.actionZoom_to.triggered.connect(self.ActionZoom_to)
        self.actionZoom_Out.triggered.connect(self.ActionZoom_Out)
        self.addLayer.clicked.connect(self.AddLayer)
        self.removeLayer.clicked.connect(self.RemoveSelected)
        self.layersModel.itemChanged.connect(self.LayerChanged)
        self.exportSvg.clicked.connect(self.ExportSVG)
        self.exportSvgPerLayer.clicked.connect(self.ExportSVGPerLayer)
        self.squigglifyTabHandler.setupSlots()

    def LoadBitmap(self):
        if self.homeFolder is None:
            from os.path import expanduser
            self.homeFolder = expanduser("~")

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

    def ActionZoom_In(self):
        # Zoom Factor
        zoomInFactor = 1.25
        self.graphicsView.scale(zoomInFactor, zoomInFactor)

    def ActionZoom_Out(self):
        # Zoom Factor
        zoomInFactor = 1 / 1.25
        self.graphicsView.scale(zoomInFactor, zoomInFactor)

    def ActionZoom_to(self):
        self.graphicsView.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def AddLayer(self):
        item = QStandardItem("Layer {0}".format(self.layersModel.rowCount() + 1))
        item.setCheckable(True)
        item.setCheckState(Qt.Checked)
        self.layersModel.appendRow(item)

    def RemoveSelected(self):
        for i in self.layersList.selectedIndexes():
            index = QPersistentModelIndex(i)
            if index in self.itemsPerLayer:
                self.scene.removeItem(self.itemsPerLayer[index])
                del self.itemsPerLayer[index]
            self.layersModel.removeRow(i.row())

    def ToggleBitmap(self):
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

    def LayerChanged(self):
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
