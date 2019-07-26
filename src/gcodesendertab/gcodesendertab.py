from tab import Tab
from os.path import expanduser
from serial import Serial
from serial.tools.list_ports import comports

class GcodeSenderTab(Tab):
    def __init__(self, parent=None, itemsPerLayer=None):
        super().__init__(parent, itemsPerLayer)
        self.homeFolder = expanduser("~")
        self.serial = Serial()
        self.serial.baudrate = 115200

    def setupSlots(self):
        self.parent.refreshPortsGcodeSender.clicked.connect(self.OnRefreshPorts)

    def OnRefreshPorts(self):
        print("YO!")
        ports = comports()
        items = ["Not connected"]
        for p in ports:
            items.append(str(p))
        self.parent.portGcodeSender.clear()
        for i in items:
            self.parent.portGcodeSender.addItem(i)
        if self.serial.is_open:
            self.serial.close()
        self.parent.portGcodeSender.setCurrentText("Not connected")


