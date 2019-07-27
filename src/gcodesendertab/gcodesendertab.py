from tab import Tab
from os.path import expanduser
from serial.tools.list_ports import comports
from os import linesep
from gcodesendertab.plotterserver import PlotterServer

SETTLING_TIME = 2.0
TIMEOUT = 10

class GcodeSenderTab(Tab):
    def __init__(self, parent=None, itemsPerLayer=None):
        super().__init__(parent, itemsPerLayer)
        self.homeFolder = expanduser("~")
        self.server = PlotterServer(self.parent.cmdFinishedGcodeSender.text().strip())
        self.paused = False
        self.item_to_device = {}

    def setupSlots(self):
        self.parent.refreshPortsGcodeSender.clicked.connect(self.OnRefreshPorts)
        self.parent.portGcodeSender.currentTextChanged.connect(self.OnSelectPort)
        self.parent.sendRawTextGcodeSender.returnPressed.connect(self.OnSendRawCommand)
        self.parent.sendTaskGcodeSender.activated.connect(self.OnSendTask)
        self.EnableDisableSendControls(False)
        self.parent.pauseGcodeSender.clicked.connect(self.OnPauseCode)
        self.parent.cancelGcodeSender.clicked.connect(self.OnCancelCode)
        self.OnRefreshPorts()

        self.server.enabledisable_send_controls.connect(self.EnableDisableSendControls)
        self.server.log.connect(self.Log)
        self.server.on_pause.connect(self.OnPauseServer)
        self.server.on_resume.connect(self.OnResumeServer)
        self.server.on_cancel.connect(self.OnCancelServer)
        self.server.on_killed.connect(self.OnKilledServer)
        self.server.on_queuesize_changed.connect(self.OnQueueSizeChanged)

    def OnQueueSizeChanged(self, newsize):
        self.parent.queueSizeGcodeSender.setText("{0}".format(newsize))

    def Log(self, msg):
        if not msg.endswith(linesep):
            msg += linesep
        #print(msg)
        self.parent.serialMonitorGcodeSender.insertPlainText(msg)
        self.parent.serialMonitorGcodeSender.ensureCursorVisible()

    def OnKilledServer(self):
        self.Log("[Server] Plotter server killed.")

    def OnConnected(self, success):
        if success:
            self.Log("[Server] Machine ready.")
        else:
            self.Log("[Server] Machine didn't initialize correctly.")

    def OnPauseCode(self):
        if self.parent.pauseGcodeSender.text() == "Pause":
            self.server.pause()
        else:
            self.server.resume()

    def OnPauseServer(self):
        self.parent.pauseGcodeSender.setText("Resume")
        self.Log("[Server] Pause program execution. Operation in progress will still complete.")

    def OnResumeServer(self):
        self.parent.pauseGcodeSender.setText("Pause")
        self.Log("[Server] Resume program execution.")

    def OnCancelCode(self):
        self.server.cancel()

    def OnCancelServer(self):
        self.Log("[Server] Cancel program execution. Operation in progress will still complete.")

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
        self.server.close()

        # select "not connected" by default
        self.parent.portGcodeSender.setCurrentText("Not connected")

    def EnableDisableSendControls(self, enable):
        self.parent.sendRawTextGcodeSender.setEnabled(enable)
        self.parent.sendSketchGcodeSender.setEnabled(enable)
        self.parent.sendByLayerGcodeSender.setEnabled(enable)
        self.parent.sendFileGcodeSender.setEnabled(enable)
        self.parent.sendTaskGcodeSender.setEnabled(enable)

    def OnSelectPort(self, newport):
        if newport and newport != "Not connected":
            startstring = self.parent.initFinishedGcodeSender.text().strip()
            baudrate = int(self.parent.baudRateGcodeSender.currentText())
            self.Log("[UI] Establishing machine connection. Please wait until finished. UI will be unresponsive during init.")
            self.EnableDisableSendControls(False)
            self.parent.application.processEvents()
            self.server.connect(newport, baudrate, self.item_to_device, startstring)
            self.server.start()
        elif newport == "Not connected":
            self.server.kill()

    def OnSendRawCommand(self):
        cmd = self.parent.sendRawTextGcodeSender.text().strip()
        self.server.submit(cmd)

    def OnSendTask(self, cmdidx):
        cmd = self.parent.sendTaskGcodeSender.itemText(cmdidx)
        task_to_code = {
            'No task selected' : '',
            'Pen up' : 'G00 {0} F{1}'.format(self.parent.penUpCmdGcode.text(), self.parent.penDownSpeedGcode.text()),
            'Pen down': 'G00 {0} F{1}'.format(self.parent.penDownCmdGcode.text(), self.parent.penDownSpeedGcode.text()),
            'Go to 0,0 (fast)' : "G00 X0 Y0",
            'Home (slowly, more accurate)' : "G00 X0 Y0|G28 X Y",
            'Move along page outline with pen up' : "G00 {0} F{1}|G00 X0 Y0|G01 X{2} Y0 F{3}|G01 X{2} Y{4}|G01 X0 Y{4}|G01 X0 Y0".format(
                self.parent.penUpCmdGcode.text(),
                self.parent.penDownSpeedGcode.text(),
                self.parent.pageWidthGcode.text().replace("M","").replace("m",""),
                self.parent.drawingSpeedGcode.text(),
                self.parent.pageHeightGcode.text().replace("M","").replace("m","")
            ),
            'Draw page outline (set up in Gcode generation tab)' : "G00 {0} F{1}|G00 X0 Y0|G28 X Y|G01 X{2} Y0 F{3}|G01 X{2} Y{4}|G01 X0 Y{4}|G01 X0 Y0".format(
                self.parent.penDownCmdGcode.text(),
                self.parent.penDownSpeedGcode.text(),
                self.parent.pageWidthGcode.text().replace("M","").replace("m",""),
                self.parent.drawingSpeedGcode.text(),
                self.parent.pageHeightGcode.text().replace("M","").replace("m","")
            ),
        }
        if cmd in task_to_code:
            code = task_to_code[cmd].split("|")
            for c in code:
                self.server.submit(c)
