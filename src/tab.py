from PyQt5.QtCore import QPersistentModelIndex, QObject, pyqtSignal
from PyQt5.QtGui import qGray, QColor, QImage
from PyQt5.QtWidgets import QMessageBox

from tab_constants import UNDEFINED


class Tab(QObject):
    """
    base class for tabs
    """
    last_used_method = pyqtSignal(QPersistentModelIndex, int)

    def __init__(self, parent=None, itemsPerLayer=None):
        super().__init__()
        self.parent = parent
        self.itemsPerLayer = itemsPerLayer

    def after_load_bitmap(self):
        """
        triggered for each tab after loading a new bitmap, e.g. to initialize some stuff
        :return:
        """
        pass

    def on_quit(self):
        """
        each tab can define cleanup actions when the program is quit
        :return:
        """
        pass

    def check_drawing_fits(self):
        """
        check if current drawing fits within defined margins
        :return:
        """
        return True

    def get_id(self):
        return UNDEFINED

    def ui_to_model(self):
        """
        each tab is to return a dict of param_name to param_value
        this can be used to save parameter values per layer when switching active layer, e.g. to save in a model file later on
        or to restore last used parameter values when switching active layer
        :return: dictionary
        """
        return {}

    def model_to_ui(self, dictionary):
        """
        each tab needs to be able to take values from a dictionary and set it into its controls
        this can be used to remember/restore parameter values per layer or from a model file
        :param dictionary: of param_name to param_value
        :return: nothing
        """
        pass

    @staticmethod
    def toBlackAndWhite(image):
        """
        convenience method to convert a color image to b&w
        :param image: any image
        :return: b&w image
        """
        newImage = QImage(image)
        for ii in range(newImage.width()):
            for jj in range(newImage.height()):
                gray = qGray(newImage.pixel(ii, jj))
                newImage.setPixel(ii, jj, QColor(gray, gray, gray).rgb())

        return newImage

    def checkBitmapLoaded(self):
        """
        convencience method to check if a bitmap has been loaded
        :return: boolean
        """
        if self.parent.bitmap is None:
            msgBox = QMessageBox()
            msgBox.setText("Please load bitmap first.")
            msgBox.exec()
            return False
        return True

    def removeOldGraphicsItems(self):
        """
        convenience method for tabs to clear graphics on current layer while maintaining internal model
        :return: nothing
        """
        layerId = QPersistentModelIndex(self.parent.layersList.currentIndex())
        if layerId not in self.itemsPerLayer:
            self.itemsPerLayer[layerId] = None
        if self.itemsPerLayer[layerId] is not None:
            self.parent.scene.removeItem(self.itemsPerLayer[layerId])

    def addNewGraphicsItems(self, group):
        """
        convencience method for tabs to add a graphics item group on current layer while maintaining internal model
        :param group: QGraphicsItemGroup
        :return: nothing
        """
        self.parent.scene.addItem(group)
        layerId = QPersistentModelIndex(self.parent.layersList.currentIndex())
        self.itemsPerLayer[layerId] = group
