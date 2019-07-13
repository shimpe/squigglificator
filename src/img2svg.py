# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'img2svg_ui.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1061, 816)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.graphicsView = MyGraphicsView(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graphicsView.sizePolicy().hasHeightForWidth())
        self.graphicsView.setSizePolicy(sizePolicy)
        self.graphicsView.setMinimumSize(QtCore.QSize(0, 500))
        self.graphicsView.setObjectName("graphicsView")
        self.squigglifySetup = QtWidgets.QTabWidget(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.squigglifySetup.sizePolicy().hasHeightForWidth())
        self.squigglifySetup.setSizePolicy(sizePolicy)
        self.squigglifySetup.setMinimumSize(QtCore.QSize(0, 250))
        self.squigglifySetup.setObjectName("squigglifySetup")
        self.squigglifySetupTab = QtWidgets.QWidget()
        self.squigglifySetupTab.setObjectName("squigglifySetupTab")
        self.label = QtWidgets.QLabel(self.squigglifySetupTab)
        self.label.setGeometry(QtCore.QRect(20, 20, 81, 18))
        self.label.setObjectName("label")
        self.invertColors = QtWidgets.QCheckBox(self.squigglifySetupTab)
        self.invertColors.setGeometry(QtCore.QRect(20, 50, 111, 22))
        self.invertColors.setObjectName("invertColors")
        self.noOfLines = QtWidgets.QSpinBox(self.squigglifySetupTab)
        self.noOfLines.setGeometry(QtCore.QRect(90, 10, 81, 32))
        self.noOfLines.setMinimum(1)
        self.noOfLines.setMaximum(5000)
        self.noOfLines.setProperty("value", 200)
        self.noOfLines.setObjectName("noOfLines")
        self.label_2 = QtWidgets.QLabel(self.squigglifySetupTab)
        self.label_2.setGeometry(QtCore.QRect(200, 20, 71, 18))
        self.label_2.setObjectName("label_2")
        self.strength = QtWidgets.QDoubleSpinBox(self.squigglifySetupTab)
        self.strength.setGeometry(QtCore.QRect(270, 10, 81, 32))
        self.strength.setMaximum(100.0)
        self.strength.setProperty("value", 5.0)
        self.strength.setObjectName("strength")
        self.detail = QtWidgets.QDoubleSpinBox(self.squigglifySetupTab)
        self.detail.setGeometry(QtCore.QRect(270, 50, 81, 32))
        self.detail.setMinimum(1.0)
        self.detail.setMaximum(10.0)
        self.detail.setProperty("value", 5.0)
        self.detail.setObjectName("detail")
        self.label_3 = QtWidgets.QLabel(self.squigglifySetupTab)
        self.label_3.setGeometry(QtCore.QRect(200, 60, 71, 18))
        self.label_3.setObjectName("label_3")
        self.lineWidthLabel = QtWidgets.QLabel(self.squigglifySetupTab)
        self.lineWidthLabel.setGeometry(QtCore.QRect(200, 100, 71, 18))
        self.lineWidthLabel.setObjectName("lineWidthLabel")
        self.lineWidth = QtWidgets.QSpinBox(self.squigglifySetupTab)
        self.lineWidth.setGeometry(QtCore.QRect(270, 90, 81, 32))
        self.lineWidth.setMinimum(1)
        self.lineWidth.setMaximum(10)
        self.lineWidth.setProperty("value", 1)
        self.lineWidth.setObjectName("lineWidth")
        self.setDefaults = QtWidgets.QPushButton(self.squigglifySetupTab)
        self.setDefaults.setGeometry(QtCore.QRect(20, 110, 88, 34))
        self.setDefaults.setObjectName("setDefaults")
        self.squigglify = QtWidgets.QToolButton(self.squigglifySetupTab)
        self.squigglify.setGeometry(QtCore.QRect(20, 150, 181, 34))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.squigglify.sizePolicy().hasHeightForWidth())
        self.squigglify.setSizePolicy(sizePolicy)
        self.squigglify.setObjectName("squigglify")
        self.verticalSquiggles = QtWidgets.QCheckBox(self.squigglifySetupTab)
        self.verticalSquiggles.setGeometry(QtCore.QRect(20, 80, 131, 22))
        self.verticalSquiggles.setObjectName("verticalSquiggles")
        self.lineWidthLabel_2 = QtWidgets.QLabel(self.squigglifySetupTab)
        self.lineWidthLabel_2.setGeometry(QtCore.QRect(380, 20, 101, 18))
        self.lineWidthLabel_2.setObjectName("lineWidthLabel_2")
        self.minBrightness = QtWidgets.QSpinBox(self.squigglifySetupTab)
        self.minBrightness.setGeometry(QtCore.QRect(480, 10, 81, 32))
        self.minBrightness.setMinimum(0)
        self.minBrightness.setMaximum(255)
        self.minBrightness.setProperty("value", 0)
        self.minBrightness.setObjectName("minBrightness")
        self.lineWidthLabel_3 = QtWidgets.QLabel(self.squigglifySetupTab)
        self.lineWidthLabel_3.setGeometry(QtCore.QRect(380, 60, 101, 18))
        self.lineWidthLabel_3.setObjectName("lineWidthLabel_3")
        self.maxBrightness = QtWidgets.QSpinBox(self.squigglifySetupTab)
        self.maxBrightness.setGeometry(QtCore.QRect(480, 50, 81, 32))
        self.maxBrightness.setMinimum(0)
        self.maxBrightness.setMaximum(255)
        self.maxBrightness.setProperty("value", 255)
        self.maxBrightness.setObjectName("maxBrightness")
        self.minStepSize = QtWidgets.QSpinBox(self.squigglifySetupTab)
        self.minStepSize.setGeometry(QtCore.QRect(480, 90, 81, 32))
        self.minStepSize.setMinimum(1)
        self.minStepSize.setMaximum(1000)
        self.minStepSize.setProperty("value", 1)
        self.minStepSize.setObjectName("minStepSize")
        self.lineWidthLabel_4 = QtWidgets.QLabel(self.squigglifySetupTab)
        self.lineWidthLabel_4.setGeometry(QtCore.QRect(380, 100, 101, 18))
        self.lineWidthLabel_4.setObjectName("lineWidthLabel_4")
        self.lineWidthLabel_5 = QtWidgets.QLabel(self.squigglifySetupTab)
        self.lineWidthLabel_5.setGeometry(QtCore.QRect(380, 140, 101, 18))
        self.lineWidthLabel_5.setObjectName("lineWidthLabel_5")
        self.maxStepSize = QtWidgets.QSpinBox(self.squigglifySetupTab)
        self.maxStepSize.setGeometry(QtCore.QRect(480, 130, 81, 32))
        self.maxStepSize.setMinimum(1)
        self.maxStepSize.setMaximum(1000)
        self.maxStepSize.setProperty("value", 10)
        self.maxStepSize.setObjectName("maxStepSize")
        self.squigglifySetup.addTab(self.squigglifySetupTab, "")
        self.bubblifySetupTab = QtWidgets.QWidget()
        self.bubblifySetupTab.setObjectName("bubblifySetupTab")
        self.bubblify = QtWidgets.QToolButton(self.bubblifySetupTab)
        self.bubblify.setGeometry(QtCore.QRect(20, 160, 181, 34))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bubblify.sizePolicy().hasHeightForWidth())
        self.bubblify.setSizePolicy(sizePolicy)
        self.bubblify.setObjectName("bubblify")
        self.setDefaultsBubblify = QtWidgets.QPushButton(self.bubblifySetupTab)
        self.setDefaultsBubblify.setGeometry(QtCore.QRect(20, 120, 88, 34))
        self.setDefaultsBubblify.setObjectName("setDefaultsBubblify")
        self.lineWidthLabel_6 = QtWidgets.QLabel(self.bubblifySetupTab)
        self.lineWidthLabel_6.setGeometry(QtCore.QRect(380, 60, 101, 18))
        self.lineWidthLabel_6.setObjectName("lineWidthLabel_6")
        self.maxBrightnessBubblify = QtWidgets.QSpinBox(self.bubblifySetupTab)
        self.maxBrightnessBubblify.setGeometry(QtCore.QRect(480, 50, 81, 32))
        self.maxBrightnessBubblify.setMinimum(0)
        self.maxBrightnessBubblify.setMaximum(255)
        self.maxBrightnessBubblify.setProperty("value", 255)
        self.maxBrightnessBubblify.setObjectName("maxBrightnessBubblify")
        self.minBrightnessBubblifyLbl = QtWidgets.QLabel(self.bubblifySetupTab)
        self.minBrightnessBubblifyLbl.setGeometry(QtCore.QRect(380, 20, 101, 18))
        self.minBrightnessBubblifyLbl.setObjectName("minBrightnessBubblifyLbl")
        self.minBrightnessBubblify = QtWidgets.QSpinBox(self.bubblifySetupTab)
        self.minBrightnessBubblify.setGeometry(QtCore.QRect(480, 10, 81, 32))
        self.minBrightnessBubblify.setMinimum(0)
        self.minBrightnessBubblify.setMaximum(255)
        self.minBrightnessBubblify.setProperty("value", 0)
        self.minBrightnessBubblify.setObjectName("minBrightnessBubblify")
        self.lineWidthLabel_8 = QtWidgets.QLabel(self.bubblifySetupTab)
        self.lineWidthLabel_8.setGeometry(QtCore.QRect(20, 60, 81, 18))
        self.lineWidthLabel_8.setObjectName("lineWidthLabel_8")
        self.minRadiusBubblify = QtWidgets.QSpinBox(self.bubblifySetupTab)
        self.minRadiusBubblify.setGeometry(QtCore.QRect(90, 10, 81, 32))
        self.minRadiusBubblify.setMinimum(1)
        self.minRadiusBubblify.setMaximum(1000)
        self.minRadiusBubblify.setProperty("value", 1)
        self.minRadiusBubblify.setObjectName("minRadiusBubblify")
        self.maxRadiusBubblify = QtWidgets.QSpinBox(self.bubblifySetupTab)
        self.maxRadiusBubblify.setGeometry(QtCore.QRect(90, 50, 81, 32))
        self.maxRadiusBubblify.setMinimum(0)
        self.maxRadiusBubblify.setMaximum(1000)
        self.maxRadiusBubblify.setProperty("value", 50)
        self.maxRadiusBubblify.setObjectName("maxRadiusBubblify")
        self.lineWidthLabel_9 = QtWidgets.QLabel(self.bubblifySetupTab)
        self.lineWidthLabel_9.setGeometry(QtCore.QRect(20, 20, 71, 18))
        self.lineWidthLabel_9.setObjectName("lineWidthLabel_9")
        self.invertColorsBubblify = QtWidgets.QCheckBox(self.bubblifySetupTab)
        self.invertColorsBubblify.setGeometry(QtCore.QRect(20, 90, 111, 22))
        self.invertColorsBubblify.setObjectName("invertColorsBubblify")
        self.lineWidthLabel_10 = QtWidgets.QLabel(self.bubblifySetupTab)
        self.lineWidthLabel_10.setGeometry(QtCore.QRect(180, 60, 101, 18))
        self.lineWidthLabel_10.setObjectName("lineWidthLabel_10")
        self.lineWidthLabel_11 = QtWidgets.QLabel(self.bubblifySetupTab)
        self.lineWidthLabel_11.setGeometry(QtCore.QRect(180, 20, 101, 18))
        self.lineWidthLabel_11.setObjectName("lineWidthLabel_11")
        self.lineWidthLabel_12 = QtWidgets.QLabel(self.bubblifySetupTab)
        self.lineWidthLabel_12.setGeometry(QtCore.QRect(180, 90, 101, 31))
        self.lineWidthLabel_12.setObjectName("lineWidthLabel_12")
        self.minProbabilityBubblify = QtWidgets.QDoubleSpinBox(self.bubblifySetupTab)
        self.minProbabilityBubblify.setGeometry(QtCore.QRect(290, 10, 81, 32))
        self.minProbabilityBubblify.setMinimum(0.01)
        self.minProbabilityBubblify.setMaximum(100.0)
        self.minProbabilityBubblify.setProperty("value", 1.0)
        self.minProbabilityBubblify.setObjectName("minProbabilityBubblify")
        self.maxProbabilityBubblify = QtWidgets.QDoubleSpinBox(self.bubblifySetupTab)
        self.maxProbabilityBubblify.setGeometry(QtCore.QRect(290, 50, 81, 32))
        self.maxProbabilityBubblify.setMinimum(0.01)
        self.maxProbabilityBubblify.setMaximum(100.0)
        self.maxProbabilityBubblify.setProperty("value", 20.0)
        self.maxProbabilityBubblify.setObjectName("maxProbabilityBubblify")
        self.radiusToleranceBubblify = QtWidgets.QDoubleSpinBox(self.bubblifySetupTab)
        self.radiusToleranceBubblify.setGeometry(QtCore.QRect(290, 90, 81, 32))
        self.radiusToleranceBubblify.setMinimum(0.01)
        self.radiusToleranceBubblify.setMaximum(1.0)
        self.radiusToleranceBubblify.setProperty("value", 0.4)
        self.radiusToleranceBubblify.setObjectName("radiusToleranceBubblify")
        self.progressBarBubblify = QtWidgets.QLabel(self.bubblifySetupTab)
        self.progressBarBubblify.setGeometry(QtCore.QRect(20, 200, 561, 18))
        self.progressBarBubblify.setObjectName("progressBarBubblify")
        self.squigglifySetup.addTab(self.bubblifySetupTab, "")
        self.horizontalLayout.addWidget(self.splitter)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1061, 30))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QDockWidget(MainWindow)
        self.toolBar.setObjectName("toolBar")
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.loadBitmap = QtWidgets.QToolButton(self.dockWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.loadBitmap.sizePolicy().hasHeightForWidth())
        self.loadBitmap.setSizePolicy(sizePolicy)
        self.loadBitmap.setObjectName("loadBitmap")
        self.verticalLayout.addWidget(self.loadBitmap)
        self.hideBitmap = QtWidgets.QPushButton(self.dockWidgetContents)
        self.hideBitmap.setObjectName("hideBitmap")
        self.verticalLayout.addWidget(self.hideBitmap)
        self.exportSvg = QtWidgets.QToolButton(self.dockWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.exportSvg.sizePolicy().hasHeightForWidth())
        self.exportSvg.setSizePolicy(sizePolicy)
        self.exportSvg.setObjectName("exportSvg")
        self.verticalLayout.addWidget(self.exportSvg)
        self.exportSvgPerLayer = QtWidgets.QPushButton(self.dockWidgetContents)
        self.exportSvgPerLayer.setObjectName("exportSvgPerLayer")
        self.verticalLayout.addWidget(self.exportSvgPerLayer)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.toolBar.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.toolBar)
        self.layers = QtWidgets.QDockWidget(MainWindow)
        self.layers.setObjectName("layers")
        self.dockWidgetContents_2 = QtWidgets.QWidget()
        self.dockWidgetContents_2.setObjectName("dockWidgetContents_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.dockWidgetContents_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.removeLayer = QtWidgets.QPushButton(self.dockWidgetContents_2)
        self.removeLayer.setObjectName("removeLayer")
        self.gridLayout.addWidget(self.removeLayer, 0, 1, 1, 1)
        self.addLayer = QtWidgets.QPushButton(self.dockWidgetContents_2)
        self.addLayer.setObjectName("addLayer")
        self.gridLayout.addWidget(self.addLayer, 0, 0, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.layersList = QtWidgets.QListView(self.dockWidgetContents_2)
        self.layersList.setAlternatingRowColors(True)
        self.layersList.setObjectName("layersList")
        self.verticalLayout_2.addWidget(self.layersList)
        self.layers.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.layers)
        self.actionLoad_Bitmap = QtWidgets.QAction(MainWindow)
        self.actionLoad_Bitmap.setObjectName("actionLoad_Bitmap")
        self.actionExport_SVG = QtWidgets.QAction(MainWindow)
        self.actionExport_SVG.setObjectName("actionExport_SVG")
        self.actionShow_toolbar = QtWidgets.QAction(MainWindow)
        self.actionShow_toolbar.setObjectName("actionShow_toolbar")
        self.actionZoom_In = QtWidgets.QAction(MainWindow)
        self.actionZoom_In.setObjectName("actionZoom_In")
        self.actionZoom_Out = QtWidgets.QAction(MainWindow)
        self.actionZoom_Out.setObjectName("actionZoom_Out")
        self.actionZoom_to = QtWidgets.QAction(MainWindow)
        self.actionZoom_to.setObjectName("actionZoom_to")
        self.actionQuit = QtWidgets.QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")
        self.actionQuit_2 = QtWidgets.QAction(MainWindow)
        self.actionQuit_2.setObjectName("actionQuit_2")
        self.actionShow_layers = QtWidgets.QAction(MainWindow)
        self.actionShow_layers.setObjectName("actionShow_layers")
        self.actionExport_SVG_one_file_per_layer = QtWidgets.QAction(MainWindow)
        self.actionExport_SVG_one_file_per_layer.setObjectName("actionExport_SVG_one_file_per_layer")
        self.menuFile.addAction(self.actionLoad_Bitmap)
        self.menuFile.addAction(self.actionExport_SVG)
        self.menuFile.addAction(self.actionExport_SVG_one_file_per_layer)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit_2)
        self.menuView.addAction(self.actionShow_toolbar)
        self.menuView.addAction(self.actionShow_layers)
        self.menuView.addSeparator()
        self.menuView.addAction(self.actionZoom_In)
        self.menuView.addAction(self.actionZoom_to)
        self.menuView.addAction(self.actionZoom_Out)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.label.setBuddy(self.noOfLines)
        self.label_2.setBuddy(self.strength)
        self.label_3.setBuddy(self.detail)
        self.lineWidthLabel.setBuddy(self.lineWidth)
        self.lineWidthLabel_2.setBuddy(self.minBrightness)
        self.lineWidthLabel_3.setBuddy(self.maxBrightness)
        self.lineWidthLabel_4.setBuddy(self.maxBrightness)
        self.lineWidthLabel_5.setBuddy(self.maxBrightness)
        self.lineWidthLabel_6.setBuddy(self.maxBrightness)
        self.minBrightnessBubblifyLbl.setBuddy(self.minBrightness)
        self.lineWidthLabel_8.setBuddy(self.maxBrightness)
        self.lineWidthLabel_9.setBuddy(self.minBrightness)
        self.lineWidthLabel_10.setBuddy(self.maxBrightness)
        self.lineWidthLabel_11.setBuddy(self.minBrightness)
        self.lineWidthLabel_12.setBuddy(self.maxBrightness)

        self.retranslateUi(MainWindow)
        self.squigglifySetup.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.loadBitmap, self.hideBitmap)
        MainWindow.setTabOrder(self.hideBitmap, self.exportSvg)
        MainWindow.setTabOrder(self.exportSvg, self.squigglifySetup)
        MainWindow.setTabOrder(self.squigglifySetup, self.noOfLines)
        MainWindow.setTabOrder(self.noOfLines, self.invertColors)
        MainWindow.setTabOrder(self.invertColors, self.verticalSquiggles)
        MainWindow.setTabOrder(self.verticalSquiggles, self.strength)
        MainWindow.setTabOrder(self.strength, self.detail)
        MainWindow.setTabOrder(self.detail, self.lineWidth)
        MainWindow.setTabOrder(self.lineWidth, self.minBrightness)
        MainWindow.setTabOrder(self.minBrightness, self.maxBrightness)
        MainWindow.setTabOrder(self.maxBrightness, self.setDefaults)
        MainWindow.setTabOrder(self.setDefaults, self.squigglify)
        MainWindow.setTabOrder(self.squigglify, self.addLayer)
        MainWindow.setTabOrder(self.addLayer, self.removeLayer)
        MainWindow.setTabOrder(self.removeLayer, self.layersList)
        MainWindow.setTabOrder(self.layersList, self.graphicsView)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Image to SVG"))
        self.label.setText(_translate("MainWindow", "No of lines"))
        self.invertColors.setText(_translate("MainWindow", "Invert Colors"))
        self.label_2.setText(_translate("MainWindow", "Strength"))
        self.label_3.setText(_translate("MainWindow", "Detail"))
        self.lineWidthLabel.setText(_translate("MainWindow", "Line width"))
        self.setDefaults.setText(_translate("MainWindow", "Set Defaults"))
        self.squigglify.setText(_translate("MainWindow", "Squigglify on selected layer"))
        self.verticalSquiggles.setText(_translate("MainWindow", "Vertical Squiggles"))
        self.lineWidthLabel_2.setText(_translate("MainWindow", "Min Brightness"))
        self.lineWidthLabel_3.setText(_translate("MainWindow", "Max Brightness"))
        self.lineWidthLabel_4.setText(_translate("MainWindow", "Min Stepsize"))
        self.lineWidthLabel_5.setText(_translate("MainWindow", "Max Stepsize"))
        self.squigglifySetup.setTabText(self.squigglifySetup.indexOf(self.squigglifySetupTab), _translate("MainWindow", "Squigglify Setup"))
        self.bubblify.setText(_translate("MainWindow", "Bubblify on selected layer"))
        self.setDefaultsBubblify.setText(_translate("MainWindow", "Set Defaults"))
        self.lineWidthLabel_6.setText(_translate("MainWindow", "Max Brightness"))
        self.minBrightnessBubblifyLbl.setText(_translate("MainWindow", "Min Brightness"))
        self.lineWidthLabel_8.setText(_translate("MainWindow", "Max radius"))
        self.lineWidthLabel_9.setText(_translate("MainWindow", "Min radius"))
        self.invertColorsBubblify.setText(_translate("MainWindow", "Invert Colors"))
        self.lineWidthLabel_10.setText(_translate("MainWindow", "Max Probability"))
        self.lineWidthLabel_11.setText(_translate("MainWindow", "Min Probability"))
        self.lineWidthLabel_12.setText(_translate("MainWindow", "Radius tolerance"))
        self.progressBarBubblify.setText(_translate("MainWindow", "Please wait while calculation is running... this may take a while!"))
        self.squigglifySetup.setTabText(self.squigglifySetup.indexOf(self.bubblifySetupTab), _translate("MainWindow", "Bubblify Setup"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuView.setTitle(_translate("MainWindow", "View"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "Toolbar"))
        self.loadBitmap.setText(_translate("MainWindow", "Load Bitmap"))
        self.hideBitmap.setText(_translate("MainWindow", "Hide Bitmap"))
        self.exportSvg.setText(_translate("MainWindow", "Export .svg all layers"))
        self.exportSvgPerLayer.setText(_translate("MainWindow", "Export .svg per layer"))
        self.layers.setWindowTitle(_translate("MainWindow", "Layers"))
        self.removeLayer.setText(_translate("MainWindow", "Remove selected"))
        self.addLayer.setText(_translate("MainWindow", "Add layer"))
        self.actionLoad_Bitmap.setText(_translate("MainWindow", "Load Bitmap"))
        self.actionExport_SVG.setText(_translate("MainWindow", "Export SVG all layers"))
        self.actionShow_toolbar.setText(_translate("MainWindow", "Show toolbar"))
        self.actionZoom_In.setText(_translate("MainWindow", "Zoom In"))
        self.actionZoom_Out.setText(_translate("MainWindow", "Zoom Out"))
        self.actionZoom_to.setText(_translate("MainWindow", "Zoom to Fit"))
        self.actionQuit.setText(_translate("MainWindow", "Quit"))
        self.actionQuit_2.setText(_translate("MainWindow", "Quit"))
        self.actionShow_layers.setText(_translate("MainWindow", "Show layers"))
        self.actionExport_SVG_one_file_per_layer.setText(_translate("MainWindow", "Export SVG one file per layer"))


from mygraphicsview import MyGraphicsView