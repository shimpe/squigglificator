from PyQt5.QtCore import QObject, pyqtSignal
from serial.serialutil import SerialException
from serial import serial_for_url
from constants import LAYER_CHANGE_CMD
from time import sleep
from os import linesep
import io
from queue import Queue, Empty
from threading import Thread

SETTLING_TIME = 2.0
TIMEOUT = 10

class PlotterServer(QObject):
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
        self.killed = True

    def start(self):
        if not self.started:
            self.killed =  False
            self.canceled = False
            self.paused = False
            self.started = True
            self.thread = Thread(target=self.process, args=(self.queue,))
            self.log.emit("[Server] Starting server...")
            self.thread.start()
            self.log.emit("[Server] Server up and running!")

    def submit(self, cmd):
        self.queue.put(cmd)
        self.on_queuesize_changed.emit(self.queue.qsize())

    def close(self):
        if self.serial and self.serial.is_open:
            self.serial.close()
            self.on_close_port.emit()

    def process(self, queue):
        while not self.killed:
            while not self.canceled:
                if self.serial:
                    while self.paused:
                        sleep(0.1)
                        if self.canceled:
                            break
                    cmd = queue.get()
                    self.on_queuesize_changed.emit(self.queue.qsize())
                    if cmd == LAYER_CHANGE_CMD:
                        self.request_layer_change.emit()
                        sleep(1.0)
                    else:
                        self.write_to_serial(cmd, self.okstring)
                    queue.task_done()
            if self.canceled:
                self.cleanup_remaining_queue_entries(queue)
                self.canceled = False

        self.cleanup_remaining_queue_entries(queue)
        self.close()
        self.on_killed.emit()

    def cleanup_remaining_queue_entries(self, queue):
        while not queue.empty():
            try:
                queue.get(False)
            except Empty:
                continue
            queue.task_done()
            self.on_queuesize_changed.emit(self.queue.qsize())

    def cancel(self):
        self.canceled = True
        self.on_cancel.emit()

    def pause(self):
        self.paused = True
        self.on_pause.emit()

    def resume(self):
        self.paused = False
        self.on_resume.emit()

    def connect(self, port, baudrate, item_to_device, init_finished_string):
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
                sleep(SETTLING_TIME) # sleep a while before accessing the port
                if self.serial.isOpen():
                    self.serial_is_open = True
                    self.on_open_port.emit()
                    self.enabledisable_send_controls.emit(True)
                    self.log.emit("[Server] Serial port {0} opened successfully.{1}Waiting for initialization to complete.{1}".format(port, linesep))
                    started = False
                    while not started:
                        sleep(0.1)
                        readval = b''
                        while self.serial.inWaiting() > 0:
                            readval += self.serial.read(1)
                        if readval:
                            #print(readval)
                            reply = str(readval, "utf-8").splitlines()
                            for r in reply:
                                self.log.emit("[Server] > {0}{1}".format(r, linesep))
                                if init_finished_string  in r:
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
