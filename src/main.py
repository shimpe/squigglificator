from PyQt5 import QtWidgets
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
