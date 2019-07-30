from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem


class LayerItem(QStandardItem):
    def __init__(self, name):
        super().__init__(name)
        self.setCheckable(True)
        self.setCheckState(Qt.Checked)
        self.parameters_per_tab = {}
        self.last_used_method = 0
        self.graphics_items = None

    def get_last_used_method(self):
        return self.last_used_method

    def set_last_used_method(self, last_used_method):
        self.last_used_method = last_used_method

    def get_parameters(self):
        return self.parameters_per_tab

    def set_parameters(self, parameters_per_tab):
        self.parameters_per_tab = parameters_per_tab

    def get_parameters_for_tab(self, tabidx):
        return self.parameters_per_tab[tabidx]

    def set_parameters_for_tab(self, tabidx, parameters):
        self.parameters_per_tab[tabidx] = parameters.copy()

    def set_graphics_items_group(self, group):
        self.graphics_items = group

    def remove_graphics_items_group(self):
        self.graphics_items = None

    def get_graphics_items_group(self):
        return self.graphics_items
