from lsystem import LSystem
from lsysteminterpreter import LSystemInterpreter
from tab import Tab


class LSystifyTab(Tab):
    def __init__(self, parent=None, itemsPerLayer=None):
        super().__init__(parent, itemsPerLayer)
        self.localBitmap = None
        self.lsystem = LSystem()
        self.lsysteminterpreter = LSystemInterpreter()

    def setupSlots(self):
        self.parent.lsystify.clicked.connect(self.process)

    def process(self):
        if not self.checkBitmapLoaded():
            return
        pass
