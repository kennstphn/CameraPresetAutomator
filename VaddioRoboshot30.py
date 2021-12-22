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
        self.attempted_preset = None
        self.storing_presets = False
        self.preset = None
        self.program = False
        self.preview = False
        self.connected = False
        self.is_moving = False
        self.needs_restart = False

        self.position_listener = threading.Thread(target=self.watch_position,
                                                  name="watch position for cam " + str(self.number))
        self.position_listener.setDaemon(True)
        self.position_listener.start()

        self.init_telnet()

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
            "is_moving": self.is_moving,
            "storing_presets": self.storing_presets,
            "preview": self.number == application.atem['preview'],
            "position": [self.pan, self.tilt, self.zoom],
            "needs_restart": self.needs_restart
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
            self.is_moving = True
            msg = "camera preset recall " + str(self.attempted_preset)
            self.tn.write(msg.encode('ascii') + b"\n")

            self.tn.read_until(b"OK")
            self.preset = self.attempted_preset
            self.is_moving = False
        except OSError:
            self.is_moving = False
            self.connected = False
            # reconnect to the server here
            self.reconnect(self.recall)

    def ask_position(self):
        self.tn.write(b"camera ptz-position get\n")
        output = self.tn.read_until(b"OK").decode('UTF-8')

        m = re.search(r"pan: ([-0-9.]+)\s*tilt: ([-0-9.]+)\s*zoom: ([-0-9.]+)\s*OK", output)
        if m is None:
            return
        self.pan = float(m.group(1))
        self.tilt = float(m.group(2))
        self.zoom = float(m.group(3))

    def store_preset(self, i):
        msg = "camera preset store " + str(i)
        self.tn.write(msg.encode('ascii') + b"\n")
        output = self.tn.read_until(b"OK", 10).decode('UTF-8')
        if re.search(r"ERROR", output):
            self.needs_restart = True

    def go_to_position(self, preset_position):
        if isinstance(preset_position, list) and preset_position.__len__() == 3:
            preset_position = PresetPosition(preset_position)

        if not isinstance(preset_position, PresetPosition):
            raise Exception('Invalid argument. Expected PresetPosition')

        ptz = preset_position
        self.is_moving = True
        command = 'camera ptz-position set pan ' + str(ptz.pan) + ' tilt ' + str(ptz.tilt) + ' zoom ' + str(ptz.zoom)
        self.tn.write(command.encode("ascii") + b"\n")
        self.tn.read_until(b"OK")
        time.sleep(.5)
        self.is_moving = False

    def load_presets(self, ptz_triple_list):
        self.storing_presets = True
        time.sleep(1)
        i = 0
        for row in ptz_triple_list:
            i = i + 1
            if row is None or len(row) == 0:
                continue
            pos = PresetPosition(row)
            self.go_to_position(pos)
            self.store_preset(i)
        self.storing_presets = False

    def make_load_preset_thread(self, ptz_triple_list):
        thread = threading.Thread(target=self.load_presets, name="loading presets for camera " + str(self.number),
                                  kwargs={
                                      "ptz_triple_list": ptz_triple_list
                                  })
        return thread

    def watch_position(self):
        while True:
            if self.connected and \
                    (self.attempted_preset == self.preset) and \
                    (not self.is_moving) and \
                    (not self.storing_presets):
                self.ask_position()
                time.sleep(.25)
            else:
                time.sleep(.25)


class PresetPosition:

    def __init__(self, ptz_triple):
        self.pan = ptz_triple[0]
        self.tilt = ptz_triple[1]
        self.zoom = ptz_triple[2]

        if not self.pan or not self.tilt or not self.zoom:
            raise Exception("Missing data in ptz_triple: " + str(ptz_triple))
