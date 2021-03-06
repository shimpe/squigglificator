import io
from os import linesep
from queue import Queue, Empty
from threading import Thread
from time import sleep

from PyQt5.QtCore import QObject, pyqtSignal
from serial import serial_for_url
from serial.serialutil import SerialException

from plotterserver_constants import LAYER_CHANGE_CMD, KILL_SERVER

SETTLING_TIME = 2.0
TIMEOUT = 10


class PlotterServer(QObject):
    """
    class to model a plotter server which allows to keep ui responsive while system is plotting
    """
    enabledisable_send_controls = pyqtSignal(bool)
    log = pyqtSignal(str)
    on_pause = pyqtSignal()
    request_layer_change = pyqtSignal()
    on_resume = pyqtSignal()
    on_cancel = pyqtSignal()
    on_killed = pyqtSignal()
    on_connected = pyqtSignal(bool)
    on_open_port = pyqtSignal()
    on_close_port = pyqtSignal()
    on_queuesize_changed = pyqtSignal(int)

    def __init__(self, okstring):
        super().__init__()
        self.serial = None
        self.sio = None
        self.paused = False
        self.canceled = False
        self.queue = Queue()
        self.okstring = okstring
        self.started = False
        self.killed = False

    def kill(self):
        """
        kill plotter server
        :return:
        """
        if self.serial and self.serial.is_open:
            self.submit(KILL_SERVER)
        self.killed = True

    def start(self):
        """
        start plotter server
        :return:
        """
        if not self.started:
            self.killed = False
            self.canceled = False
            self.paused = False
            self.started = True
            self.thread = Thread(target=self.process, args=(self.queue,))
            self.log.emit("[Server] Starting server...")
            self.thread.start()
            self.log.emit("[Server] Server up and running!")

    def submit(self, cmd):
        """
        submit command to plotter server thread
        :param cmd: a string of gcode or a server command; supported server commands are defined in plotterserver_constants.py
        :return:
        """
        self.queue.put(cmd)
        self.on_queuesize_changed.emit(self.queue.qsize())

    def close(self):
        """
        close serial connection
        :return:
        """
        if self.serial and self.serial.is_open:
            self.serial.close()
            self.on_close_port.emit()

    def process(self, queue):
        """
        the plotter server command loop running in separate thread and processing commands
        :param queue:
        :return:
        """
        while not self.killed:
            while not self.canceled:
                if self.serial:
                    while self.paused:
                        sleep(0.1)
                        if self.canceled:
                            break
                        if self.killed:
                            break
                    cmd = queue.get()
                    self.on_queuesize_changed.emit(self.queue.qsize())
                    if cmd == LAYER_CHANGE_CMD:
                        self.request_layer_change.emit()
                        sleep(1.0)
                    elif cmd == KILL_SERVER:
                        self.killed = True
                        break
                    else:
                        self.write_to_serial(cmd, self.okstring)
                    queue.task_done()
                if self.killed:
                    break
            if self.canceled:
                self.cleanup_remaining_queue_entries(queue)
                self.canceled = False
                self.paused = False

        self.cleanup_remaining_queue_entries(queue)
        self.close()
        self.on_killed.emit()

    def cleanup_remaining_queue_entries(self, queue):
        """
        remove remaining items from command queue, useful for cancellation or when quitting
        :param queue:
        :return:
        """
        while not queue.empty():
            try:
                queue.get(False)
            except Empty:
                continue
            queue.task_done()
            self.on_queuesize_changed.emit(self.queue.qsize())

    def cancel(self):
        """
        ask server to cancel current plot job
        :return:
        """
        self.canceled = True
        self.on_cancel.emit()

    def pause(self):
        """
        ask server to pause current plot job
        :return:
        """
        self.paused = True
        self.on_pause.emit()

    def resume(self):
        """
        ask server to resume current plot job
        :return:
        """
        self.paused = False
        self.on_resume.emit()

    def connect(self, port, baudrate, item_to_device, init_finished_string):
        """
        connect to serial port to talk to machine
        :param port: descriptive name of the serial port
        :param baudrate:
        :param item_to_device: dictionary from descriptive name of serial devices to OS name of serial devices
        :param init_finished_string: string to wait for to indicate machine is initialized
        :return:
        """
        if port == "":
            return
        if port == "Not connected":
            self.close()
            return
        if port in item_to_device:
            device = item_to_device[port]
            self.serial = serial_for_url(device)
            self.close()
            self.serial.port = device
            self.serial.timeout = TIMEOUT
            self.serial.baudrate = baudrate
            try:
                self.serial.open()
                sleep(SETTLING_TIME)  # sleep a while before accessing the port
                if self.serial.isOpen():
                    self.serial_is_open = True
                    self.on_open_port.emit()
                    self.enabledisable_send_controls.emit(True)
                    self.log.emit(
                        "[Server] Serial port {0} opened successfully.{1}Waiting for initialization to complete.{1}".format(
                            port, linesep))
                    started = False
                    while not started:
                        sleep(0.1)
                        readval = b''
                        while self.serial.inWaiting() > 0:
                            readval += self.serial.read(1)
                        if readval:
                            # print(readval)
                            reply = str(readval, "utf-8").splitlines()
                            for r in reply:
                                self.log.emit("[Server] > {0}{1}".format(r, linesep))
                                if init_finished_string in r:
                                    started = True
                    self.sio = io.TextIOWrapper(io.BufferedRWPair(self.serial, self.serial, 1))
                    self.on_connected.emit(True)
                else:
                    self.log.emit("[Server] Error opening serial port. Unknown reason.")

            except SerialException as e:
                self.serial_is_open = False
                self.on_connected.emit(False)
                self.enabledisable_send_controls(False)
                self.log.emit("[Server] Error opening serial port: {0}".format(e.strerror))
        else:
            print("[Server] port = '{0}' not present in {1}".format(port, item_to_device.keys()))

    def write_to_serial(self, cmd, okstring):
        """
        write a command to the serial port
        :param cmd:
        :param okstring: string to expect to be returned when command is processed
        :return:
        """
        original_cmd = cmd[:]
        cmd = cmd.split("(")[0]  # cut off comments
        cmd = cmd.split(";")[0]  # cut off comments
        cmd = cmd.strip().upper()
        if cmd:
            if self.serial_is_open:
                cmd = cmd + linesep
                self.log.emit("[Server] < " + original_cmd)
                self.sio.write(cmd)
                self.sio.flush()  # it is buffering. required to get the data out *now*
                ok = False
                maxattempts = 10000
                attempt = 0
                while not ok and attempt < maxattempts:
                    sleep(0.01)
                    readval = ''
                    while self.serial.inWaiting() > 0:
                        readval += self.serial.readline().decode("ascii")
                    if readval:
                        reply = readval.splitlines()
                        for r in reply:
                            self.log.emit("[Server] > {0}{1}".format(r, linesep))
                            if okstring in r:
                                ok = True
                if not ok:
                    self.log.emit("[Server] ERROR: TIMEOUT waiting for reply reported by plotter server")
            else:
                self.log.emit("[Server] ERROR! Serial port not open." + linesep)
