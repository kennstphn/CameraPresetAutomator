import telnetlib
import threading
import time
import Switcher
import application


class Camera:
    def __init__(self, ip, user, password, number):
        self.ip = ip
        self.number = number
        self.user = user
        self.password = password
        self.tn = None
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
        return None

    def is_live(self):
        return self.number == application.atem['program'] or (
                        self.number == application.atem['preview'] and application.atem['inTransition']
            )

    def reconnect(self, then=None, args=None):
        thread = threading.Thread(None, self.init_telnet, self.ip, [then, args])
        thread.setDaemon(True)
        thread.start()

    def toJson(self):
        return {
            "ip": self.ip,
            "number": self.number,
            "preset": self.preset,
            "attempted_preset": self.attempted_preset,
            "connected": self.connected,
            "program":self.is_live(),
            "preview": self.number == application.atem['preview']
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
        thread = threading.Thread(target=self.wait_program_then_recall, name="recalling preset")
        thread.setDaemon(True)
        thread.start()

    def recall(self):
        if self.attempted_preset == self.preset:
            print(self.preset + " is already = " + self.attempted_preset)
            return
        try:
            print("recalling...")
            msg = "camera preset recall " + str(self.attempted_preset)
            self.tn.write(msg.encode('ascii') + b"\n")
            print("system write done")
            self.tn.read_until(b"OK")
            print("system OK")
            self.preset = self.attempted_preset
        except OSError:
            # reconnect to the server here
            self.reconnect(self.recall)
