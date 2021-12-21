import rtmidi
import threading


class Collector(threading.Thread):

    def __init__(self, device, port):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.port = port
        self.portName = device.getPortName(port)
        self.device = device
        self.quit = False

    def run(self):
        self.device.openPort(self.port)
        self.device.ignoreTypes(True, False, True)
        while True:
            if self.quit:
                return
            msg = self.device.getMessage()
            if not msg:
                continue
            if msg.isNoteOn():
                mode = 'ON'
            elif msg.isNoteOff():
                mode = 'OFF'
            elif msg.isController():
                mode = 'CC'
            else:
                mode = 'N/A'
            note = msg.getNoteNumber()
            velocity = msg.getVelocity()
            issue(self.portName, note, mode, velocity)


subscribers = []


def subscribe_to_midi_notes(callback):
    subscribers.append(callback)


def issue(port, note, mode, velocity):
    for subscriber in subscribers:
        subscriber(port=port, note=note, mode=mode, velocity=velocity)


for i in range(rtmidi.RtMidiIn().getPortCount()):
    Collector(
        rtmidi.RtMidiIn()
        , i
    ).start()
