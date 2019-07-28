from tab import Tab
from os.path import expanduser
from serial.tools.list_ports import comports
from os import linesep
from gcodesendertab.plotterserver import PlotterServer
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from time import sleep

SETTLING_TIME = 2.0
TIMEOUT = 10

class GcodeSenderTab(Tab):
    """
    tab to implement a gcode sender
    """
    def __init__(self, parent=None, itemsPerLayer=None):
        super().__init__(parent, itemsPerLayer)
        self.homeFolder = expanduser("~")
        self.server = PlotterServer(self.parent.cmdFinishedGcodeSender.text().strip())
        self.paused = False
        self.item_to_device = {}

    def setupSlots(self):
        """
        set up slots to make the buttons do something
        :return:
        """
        self.parent.refreshPortsGcodeSender.clicked.connect(self.OnRefreshPorts)
        self.parent.portGcodeSender.currentTextChanged.connect(self.OnSelectPort)
        self.parent.sendRawTextGcodeSender.returnPressed.connect(self.OnSendRawCommand)
        self.parent.sendTaskGcodeSender.activated.connect(self.OnSendTask)
        self.parent.sendFileGcodeSender.clicked.connect(self.OnSendFile)
        self.parent.sendSketchGcodeSender.clicked.connect(self.OnSendSketch)
        self.parent.sendByLayerGcodeSender.clicked.connect(self.OnSendByLayer)
        self.EnableDisableSendControls(False)
        self.parent.pauseGcodeSender.clicked.connect(self.OnPauseCode)
        self.parent.cancelGcodeSender.clicked.connect(self.OnCancelCode)
        self.OnRefreshPorts()

        self.server.enabledisable_send_controls.connect(self.EnableDisableSendControls)
        self.server.log.connect(self.Log)
        self.server.on_pause.connect(self.OnPauseServer)
        self.server.request_layer_change.connect(self.RequestPause)
        self.server.on_resume.connect(self.OnResumeServer)
        self.server.on_cancel.connect(self.OnCancelServer)
        self.server.on_killed.connect(self.OnKilledServer)
        self.server.on_queuesize_changed.connect(self.OnQueueSizeChanged)

    def on_quit(self):
        """
        kill plotter server when it's time to quit
        :return:
        """
        self.server.kill()

    def OnQueueSizeChanged(self, newsize):
        """
        slot used to visualize signal emitted by plotter server
        :param newsize:
        :return:
        """
        self.parent.queueSizeGcodeSender.setText("{0}".format(newsize))

    def Log(self, msg):
        """
        slot used to visualize signal emitted by plotter server
        :param msg: string to log into the serial monitor
        :return:
        """
        if not msg.endswith(linesep):
            msg += linesep
        #print(msg)
        self.parent.serialMonitorGcodeSender.insertPlainText(msg)
        self.parent.serialMonitorGcodeSender.ensureCursorVisible()

    def OnKilledServer(self):
        """
        slot used to visualize signal emitted by plotter server
        :return:
        """
        self.Log("[Server] Plotter server killed.")

    def OnConnected(self, success):
        """
        slot used to visualize signal emitted by plotter server
        :param success:
        :return:
        """
        if success:
            self.Log("[Server] Machine ready.")
        else:
            self.Log("[Server] Machine didn't initialize correctly.")

    def OnPauseCode(self):
        """
        handler for user pressing pause button in ui
        :return:
        """
        if self.parent.pauseGcodeSender.text() == "Pause":
            self.server.pause()
        else:
            self.server.resume()

    def RequestPause(self):
        """
        handler for plotter server requesting pressing pause button during plotting
        :return:
        """
        self.Log("[Server] Requesting layer change. Please resume when ready to start next layer.")
        self.server.pause()

    def OnPauseServer(self):
        """
        handler for signal emitted by server after having received pause request
        :return:
        """
        self.parent.pauseGcodeSender.setText("Resume")
        self.Log("[Server] Pause program execution. Operation in progress will still complete.")

    def OnResumeServer(self):
        """
        handler for signal emitted by server after having received resume request
        :return:
        """
        self.parent.pauseGcodeSender.setText("Pause")
        self.Log("[Server] Resume program execution.")

    def OnCancelCode(self):
        """
        handler for user pressing Cancel button in ui
        :return:
        """
        self.server.cancel()

    def OnCancelServer(self):
        """
        handler for signal emitted by server after having received cancel request
        :return:
        """
        self.Log("[Server] Cancel program execution. Operation in progress will still complete.")

    def OnRefreshPorts(self):
        """
        handler for user pressing refresh ports button in ui
        :return:
        """
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
        """
        convenience method for enabling/disabling all gcode sending related controls at once
        :param enable:
        :return:
        """
        self.parent.sendRawTextGcodeSender.setEnabled(enable)
        self.parent.sendSketchGcodeSender.setEnabled(enable)
        self.parent.sendByLayerGcodeSender.setEnabled(enable)
        self.parent.sendFileGcodeSender.setEnabled(enable)
        self.parent.sendTaskGcodeSender.setEnabled(enable)

    def OnSelectPort(self, newport):
        """
        handler for user selecting a different usb/serial port in ui
        :param newport:
        :return:
        """
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
        """
        handler for user sending a manual command to plotter server
        :return:
        """
        cmd = self.parent.sendRawTextGcodeSender.text().strip()
        self.server.submit(cmd)

    def OnSendTask(self, cmdidx):
        """
        handler for user sending a predefined task to plotter server via UI
        :param cmdidx: index of selected task in combobox
        :return:
        """
        cmd = self.parent.sendTaskGcodeSender.itemText(cmdidx)
        task_to_code = {
            'No task selected' : '',
            'Pen up' : 'G00 {pu} F{ps}'.format(pu=self.parent.penUpCmdGcode.text(), ps=self.parent.penDownSpeedGcode.text()),
            'Pen down': 'G00 {pd} F{ps}'.format(pd=self.parent.penDownCmdGcode.text(), ps=self.parent.penDownSpeedGcode.text()),
            'Go to 0,0 (fast)' : "G00 X0 Y0",
            'Home (slow and accurate)' : "G00 X0 Y0|G28 X Y",
            'Move along page outline with pen up' : "G00 {pu} F{ps}|G00 X0 Y0|G01 X{pw} Y0 F{ds}|G01 X{pw} Y{ph}|G01 X0 Y{ph}|G01 X0 Y0".format(
                pu=self.parent.penUpCmdGcode.text(),
                ps=self.parent.penDownSpeedGcode.text(),
                pw=self.parent.pageWidthGcode.text().replace("M","").replace("m",""),
                ds=self.parent.drawingSpeedGcode.text(),
                ph=self.parent.pageHeightGcode.text().replace("M","").replace("m","")
            ),
            'Draw page outline (set up in Gcode generation tab)' : "G00 {pd} F{ps}|G00 X0 Y0|G01 X{pw} Y0 F{ds}|G01 X{pw} Y{ph}|G01 X0 Y{ph}|G01 X0 Y0".format(
                pd=self.parent.penDownCmdGcode.text(),
                ps=self.parent.penDownSpeedGcode.text(),
                pw=self.parent.pageWidthGcode.text().replace("M","").replace("m",""),
                ds=self.parent.drawingSpeedGcode.text(),
                ph=self.parent.pageHeightGcode.text().replace("M","").replace("m","")
            ),
            'Draw page margins (set up in Gcode generation tab)' : "G00 {pu} F{ps}|G00 X{lx} Y{by}|G00 {pd} F{ps}|G01 X{rx} Y{by} F{ds}|G01 X{rx} Y{ty}|G01 X{lx} Y{ty}|G01 X{lx} Y{by}".format(
                pu=self.parent.penUpCmdGcode.text(),
                ps=self.parent.penDownSpeedGcode.text(),
                pd=self.parent.penDownCmdGcode.text(),
                ds=self.parent.drawingSpeedGcode.text(),
                lx=self.parent.xMarginGcode.value(),
                by=self.parent.yMarginGcode.value(),
                rx=float(self.parent.pageWidthGcode.text().replace("M","").replace("m",""))-self.parent.xMarginGcode.value(),
                ty=float(self.parent.pageHeightGcode.text().replace("M","").replace("m",""))-self.parent.yMarginGcode.value()
            ),
            'Mark page corners (set up in Gcode generation tab)' : "G00 {pu} F{ps}|G00 X0 Y10           |G00 {pd} F{ps}|G01 X0 Y0 F{ds}      |G01 X10 Y0|"
                                                                   "G00 {pu} F{ps}|G00 X{pwminten} Y0   |G00 {pd} F{ps}|G01 X{pw} Y0 F{ds}   |G01 X{pw} Y10|"
                                                                   "G00 {pu} F{ps}|G00 X{pw} Y{phminten}|G00 {pd} F{ps}|G01 X{pw} Y{ph} F{ds}|G01 X{pwminten} Y{ph}|"
                                                                   "G00 {pu} F{ps}|G00 X10 Y{ph}        |G00 {pd} F{ps}|G01 X0 Y{ph} F{ds}   |G01 X0 Y{phminten}|"
                                                                   "G00 {pu} F{ps}|G00 X0 Y0".format(
                pu=self.parent.penUpCmdGcode.text(),
                pd=self.parent.penDownCmdGcode.text(),
                ps=self.parent.penDownSpeedGcode.text(),
                pw=self.parent.pageWidthGcode.text().replace("M","").replace("m",""),
                pwminten=float(self.parent.pageWidthGcode.text().replace("M","").replace("m",""))-10,
                ph=self.parent.pageHeightGcode.text().replace("M", "").replace("m", ""),
                phminten=float(self.parent.pageHeightGcode.text().replace("M", "").replace("m", "")) - 10,
                ds=self.parent.drawingSpeedGcode.text(),
            ),
            'Draw empty music paper (hah! didn\'t see that one coming did you!?)' : ""
        }
        if cmd in task_to_code:
            code = task_to_code[cmd].split("|")
            for c in code:
                self.server.submit(c.strip())

    def OnSendFile(self):
        """
        handler for user clicking the send file button in the ui
        :return:
        """
        loadpath = QFileDialog.getOpenFileName(self.parent.centralwidget, "Load .cnc file",
                                              self.homeFolder,
                                              "CNC files (*.cnc)")
        if not loadpath[0]:
            return

        percentage_lines = 0
        with open(loadpath[0], "r") as f:
            for line in f.readlines():
                percentage_lines = self.submit_line(line, percentage_lines)

    def submit_line(self, line, percentage_lines):
        """
        send a line of code (or a server command) to the plotter server
        :param line:
        :param percentage_lines:
        :return:
        """
        # filter out the % lines (start/stop of file)
        if line.strip() == "%":
            percentage_lines += 1  # no need to submit to plotter server
        else:
            # everything after second % is ignored
            if percentage_lines < 2:
                self.server.submit(line)
        return percentage_lines

    def OnSendSketch(self):
        """
        handler for user clicking send sketch button in ui
        :return:
        """
        margin_errors = self.parent.check_drawing_fits()
        ret = QMessageBox.Cancel
        if margin_errors:
            msg_box = QMessageBox()
            msg_box.setText("Warning! With current scaling, bitmap doesn't fit between the defined margins ({0}). Abort?".format(" and ".join(margin_errors)))
            msg_box.setInformativeText("Do you want to abort plotting?")
            msg_box.setStandardButtons(QMessageBox.Ok |QMessageBox.Cancel)
            msg_box.setDefaultButton(QMessageBox.Ok)
            ret = msg_box.exec()

        if ret == QMessageBox.Cancel:
            self.Log("[UI] Please wait while code is being generated.")
            self.parent.application.processEvents()
            gen = self.parent.get_sketch_code()
            percentage_lines = 0
            for line in gen.code.splitlines():
                percentage_lines = self.submit_line(line, percentage_lines)
        else:
            self.Log("[UI] Aborting.")

    def OnSendByLayer(self):
        """
        handler for user clicking send by layer button in ui
        :return:
        """
        margin_errors = self.parent.check_drawing_fits()
        ret = QMessageBox.Cancel
        if margin_errors:
            msg_box = QMessageBox()
            msg_box.setText("Warning! With current scaling, bitmap doesn't fit between the defined margins ({0}). Abort?".format(" and ".join(margin_errors)))
            msg_box.setInformativeText("Do you want to abort plotting?")
            msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msg_box.setDefaultButton(QMessageBox.Ok)
            ret = msg_box.exec()

        if ret == QMessageBox.Cancel:
            self.Log("[UI] Please wait while code is being generated.")
            self.parent.application.processEvents()
            list_of_gen = self.parent.get_sketch_by_layer()
            for idx,gen in enumerate(list_of_gen):
                percentage_lines = 0
                self.submit_line("%%% Layer change", percentage_lines)
                for line in gen.code.splitlines():
                    percentage_lines = self.submit_line(line, percentage_lines)
