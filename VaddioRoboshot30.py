import telnetlib
import threading
import time
import application
import re


class Camera:
    def __init__(self, ip, user, password, number):
        self.ip = ip
        self.pan = 0.0
        self.tilt = 0.0
        self.zoom = 0.0
        self.number = number
        self.user = user
        self.password = password
        self.tn = None
        self.tn2 = None
        self.attempted_preset = None
        self.preset = None
        self.program = False
        self.preview = False
        self.connected = False
        self.reconnect()

    def wait_program_then_recall(self):
        while self.is_live():
            time.sleep(1 / 60)
        self.recall()

    def init_telnet(self, then=None, args=None):
        self.connected = False
        self.tn = telnetlib.Telnet(self.ip)
        self.tn.read_until(b"login: ")
        self.tn.write(self.user.encode('ascii') + b"\n")
        self.tn.read_until(b"Password: ")
        self.tn.write(self.password.encode('ascii') + b"\n")
        self.tn.read_until(b"Welcome admin")
        self.connected = True
        if then:
            if args is None:
                args = []
            then(args=args)
        self.ask_position()
        return None

    def is_live(self):
        return self.number == application.atem['program'] or (
                self.number == application.atem['preview'] and application.atem['inTransition']
        )

    def reconnect(self, then=None, args=None):
        print("reconnecting camera " + str(self.number))
        thread = threading.Thread(target=self.init_telnet, name=self.ip, kwargs={"then": then, "args": args})
        thread.setDaemon(True)
        thread.start()

    def toJson(self):
        return {
            "ip": self.ip,
            "number": self.number,
            "preset": self.preset,
            "attempted_preset": self.attempted_preset,
            "connected": self.connected,
            "program": self.is_live(),
            "preview": self.number == application.atem['preview'],
            "position": [self.pan, self.tilt, self.zoom]
        }

    def set_tally(self, preview_or_program, t_or_f):
        if preview_or_program == "preview":
            self.preview = bool(t_or_f)
        elif preview_or_program == "program":
            self.program = bool(t_or_f)
        else:
            raise Exception("invalid data for preview_or_program")

    def handle_midi_note(self, port, note, mode, velocity):
        if mode != "ON":
            print("mode is not ON")
            return
        if note not in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]:
            print('note is not 1-16')
            return
        self.attempted_preset = note
        thread = threading.Thread(target=self.wait_program_then_recall, name="recalling for camera " + str(self.number))
        thread.setDaemon(True)
        thread.start()

    def recall(self):
        if self.attempted_preset == self.preset:
            return
        try:
            msg = "camera preset recall " + str(self.attempted_preset)
            self.tn.write(msg.encode('ascii') + b"\n")

            self.tn.read_until(b"OK")
            self.preset = self.attempted_preset
            self.ask_position()
        except OSError:
            self.connected = False
            # reconnect to the server here
            self.reconnect(self.recall)

    def ask_position(self):
        self.tn.write(b"camera pan get\n")
        self.tn.read_until(b"camera pan get")
        output = self.tn.read_until(b"OK")
        output = output.decode('UTF-8')
        m = re.search(r"\u001b\[0m(.*)\u001b", output)
        self.pan = float(m.group(1))

        self.tn.write(b"camera tilt get\n")
        self.tn.read_until(b"camera tilt get")
        output = self.tn.read_until(b"OK")
        output = output.decode('UTF-8')
        m = re.search(r"\u001b\[0m(.*)\u001b", output)
        if m is not None:
            self.tilt = float(m.group(1))

        self.tn.write(b"camera zoom get\n")
        self.tn.read_until(b"camera zoom get")
        output = self.tn.read_until(b"OK")
        output = output.decode('UTF-8')
        m = re.search(r"\u001b\[0m(.*)\u001b", output)
        self.tilt = float(m.group(1))


    def store_preset(self, i):
        msg = "camera preset store " + str(i)
        self.tn.write(msg.encode('ascii') + b"\n")
        self.tn.read_until(b"OK")
