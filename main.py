from PyQt5 import QtCore, QtGui, QtWidgets
from mygraphicsview import MyGraphicsView
from mymainwindow import MyMainWindow

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = MyMainWindow()
    ui.setupUi(MainWindow)
    ui.finishSetupUi()
    ui.setupSlots()
    MainWindow.show()
    sys.exit(app.exec_())
