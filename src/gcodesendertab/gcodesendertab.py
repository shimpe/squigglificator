from tab import Tab
from os import linesep
from os.path import expanduser
from serial import Serial
from serial.tools.list_ports import comports
from serial.serialutil import SerialException
from serial import serial_for_url
from PyQt5.QtWidgets import QMessageBox
import time
import io

SETTLING_TIME = 2.0
TIMEOUT = 10

class GcodeSenderTab(Tab):
    def __init__(self, parent=None, itemsPerLayer=None):
        super().__init__(parent, itemsPerLayer)
        self.homeFolder = expanduser("~")
        self.item_to_device = {}
        self.serial = None
        self.sio = None

        self.paused = False
        self.canceled = False

    def setupSlots(self):
        self.parent.refreshPortsGcodeSender.clicked.connect(self.OnRefreshPorts)
        self.parent.portGcodeSender.currentTextChanged.connect(self.OnSelectPort)
        self.parent.sendRawTextGcodeSender.returnPressed.connect(self.OnSendRawCommand)
        self.parent.sendTaskGcodeSender.currentTextChanged.connect(self.OnSendTask)
        self.EnableDisableSendControls(False)
        self.parent.pauseGcodeSender.clicked.connect(self.OnPauseCode)
        self.parent.cancelGcodeSender.clicked.connect(self.OnCancelCode)
        self.OnRefreshPorts()

    def OnPauseCode(self):
        self.paused = not self.paused
        self.parent.pauseGcodeSender.setText("Resume" if self.paused else "Pause")

    def OnCancelCode(self):
        self.canceled = True

    def OnRefreshPorts(self):
        ports = comports()

        # remove old items
        self.parent.portGcodeSender.clear()
        self.item_to_device = {}

        # collect new items
        items = ["Not connected"]
        for p in ports:
            items.append(str(p))
            self.item_to_device[str(p)] = p.device

        # set items in combobox
        for i in items:
            self.parent.portGcodeSender.addItem(i)

        # close existing connection if any
        if self.serial and self.serial.is_open:
            self.serial.close()

        # select "not connected" by default
        self.parent.portGcodeSender.setCurrentText("Not connected")

    def EnableDisableSendControls(self, enable):
        self.parent.sendRawTextGcodeSender.setEnabled(enable)
        self.parent.sendSketchGcodeSender.setEnabled(enable)
        self.parent.sendByLayerGcodeSender.setEnabled(enable)
        self.parent.sendFileGcodeSender.setEnabled(enable)
        self.parent.sendTaskGcodeSender.setEnabled(enable)

    def OnSelectPort(self, newport):
        startstring = self.parent.initFinishedGcodeSender.text().strip()
        baudrate = int(self.parent.baudRateGcodeSender.currentText())
        self.EnableDisableSendControls(False)
        if newport == "":
            return
        if newport == "Not connected":
            if self.serial and self.serial.is_open:
                self.serial.close()
            return
        if newport in self.item_to_device:
            device = self.item_to_device[newport]
            self.serial = serial_for_url(device)
            if self.serial and self.serial.is_open:
                self.serial.close()
            self.serial.port = device
            self.serial.timeout = TIMEOUT
            self.serial.baudrate = baudrate
            try:
                self.serial.open()
                time.sleep(SETTLING_TIME) # sleep a while before accessing the port
                if self.serial.isOpen():
                    self.serial_is_open = True
                    self.EnableDisableSendControls(True)
                    self.parent.serialMonitorGcodeSender.insertPlainText("Serial port {0} opened successfully.{1}Waiting for initialization to complete.{1}".format(newport, linesep))
                    started = False
                    while not started:
                        time.sleep(0.1)
                        readval = b''
                        while self.serial.inWaiting() > 0:
                            readval += self.serial.read(1)
                        if readval:
                            #print(readval)
                            reply = str(readval, "utf-8").splitlines()
                            for r in reply:
                                self.parent.serialMonitorGcodeSender.insertPlainText("> {0}{1}".format(r, linesep))
                                self.parent.application.processEvents()
                                if startstring  in r:
                                    started = True
                    self.parent.serialMonitorGcodeSender.insertPlainText("> Machine initialized."+linesep)
                    self.sio = io.TextIOWrapper(io.BufferedRWPair(self.serial, self.serial, 1))
                else:
                    msg_box = QMessageBox()
                    msg_box.setText("Error opening serial port. Unknown reason.");
                    msg_box.exec()

            except SerialException as e:
                self.serial_is_open = False
                self.EnableDisableSendControls(False)
                msg_box = QMessageBox()
                msg_box.setText("Error opening serial port: {0}".format(e.strerror));
                msg_box.exec()
        else:
            print("newport = '{0}' not present in {1}".format(newport, self.item_to_device.keys()))

    def write_to_serial(self, cmd):
        cmd = cmd.split("(")[0]  # cut off comments
        cmd = cmd.split(";")[0]  # cut off comments
        cmd = cmd.strip().upper()
        if cmd:
            okstring = self.parent.cmdFinishedGcodeSender.text().strip()
            if self.serial_is_open:
                cmd = cmd + linesep
                self.parent.serialMonitorGcodeSender.insertPlainText("< " + cmd)
                self.parent.application.processEvents()
                self.sio.write(cmd)
                self.sio.flush()  # it is buffering. required to get the data out *now*
                ok = False
                maxattempts = 10000
                attempt = 0
                while not ok and attempt < maxattempts:
                    time.sleep(0.01)
                    readval = ''
                    while self.serial.inWaiting() > 0:
                        readval += self.serial.readline().decode("ascii")
                    if readval:
                        #print(readval)
                        reply = readval.splitlines()
                        for r in reply:
                            self.parent.serialMonitorGcodeSender.insertPlainText("> {0}{1}".format(r, linesep))
                            self.parent.serialMonitorGcodeSender.ensureCursorVisible()
                            self.parent.application.processEvents()
                            if okstring in r:
                                ok = True
                if not ok:
                    self.parent.serialMonitorGcodeSender.insertPlainText("ERROR: TIMEOUT?!")
                    self.parent.application.processEvents()
            else:
                self.parent.serialMonitorGcodeSender.insertPlainText("ERROR! Serial port not open." + linesep)

    def OnSendRawCommand(self):
        cmd = self.parent.sendRawTextGcodeSender.text().strip()
        self.write_to_serial(cmd)

    def OnSendTask(self):
        cmd = self.parent.sendTaskGcodeSender.currentText()
        task_to_code = {
            'No task selected' : '',
            'Pen up' : 'G00 {0} F{1}'.format(self.parent.penUpCmdGcode.text(), self.parent.penDownSpeedGcode.text()),
            'Pen down': 'G00 {0} F{1}'.format(self.parent.penDownCmdGcode.text(), self.parent.penDownSpeedGcode.text()),
            'Go to 0,0 (fast)' : "G00 X0 Y0",
            'Home (slowly, more accurate)' : "G00 X0 Y0|G28 X Y",
            'Move along page outline with pen up' : "G00 {0} F{1}|G00 X0 Y0|G28 X Y|G01 X{2} Y0 F{3}|G01 X{2} Y{4}|G01 X0 Y{4}|G01 X0 Y0".format(
                self.parent.penUpCmdGcode.text(),
                self.parent.penDownSpeedGcode.text(),
                self.parent.pageWidthGcode.text(),
                self.parent.drawingSpeedGcode.text(),
                self.parent.pageHeightGcode.text()
            ),
            'Draw page outline (set up in Gcode generation tab)' : "G00 {0} F{1}|G00 X0 Y0|G28 X Y|G01 X{2} Y0 F{3}|G01 X{2} Y{4}|G01 X0 Y{4}|G01 X0 Y0".format(
                self.parent.penDownCmdGcode.text(),
                self.parent.penDownSpeedGcode.text(),
                self.parent.pageWidthGcode.text(),
                self.parent.drawingSpeedGcode.text(),
                self.parent.pageHeightGcode.text()
            ),
        }
        if cmd in task_to_code:
            code = task_to_code[cmd].split("|")
            for c in code:
                while self.paused:
                    self.parent.application.processEvents()
                    time.sleep(0.01)
                    if self.canceled:
                        self.OnPauseCode() # untoggle pause button again
                        break
                if self.canceled:
                    self.canceled = False
                    break
                self.write_to_serial(c)
