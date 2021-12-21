import VaddioRoboshot30
import ProPresenter7

camera1 = VaddioRoboshot30.Camera('192.168.1.10', 'admin', 'password', 1)
camera2 = VaddioRoboshot30.Camera('192.168.1.4', 'admin', 'password', 2)
camera3 = VaddioRoboshot30.Camera('192.168.1.20', 'admin', 'password', 3)
camera4 = VaddioRoboshot30.Camera('192.168.1.22', 'admin', 'password', 4)
camera5 = VaddioRoboshot30.Camera('192.168.1.24', 'admin', 'password', 5)


def update_camera_tally(camera_number, tally, tf):
    if camera_number == 1:
        camera1.set_tally(tally, tf)
    elif camera_number == 2:
        camera2.set_tally(tally, tf)
    elif camera_number == 3:
        camera3.set_tally(tally, tf)
    elif camera_number == 4:
        camera4.set_tally(tally, tf)
    elif camera_number == 5:
        camera5.set_tally(tally, tf)
    else:
        print('no camera found for ' + str(camera_number))
        return None


ProPresenter7.subscribe_to_midi_notes(camera1.handle_midi_note)
ProPresenter7.subscribe_to_midi_notes(camera2.handle_midi_note)
ProPresenter7.subscribe_to_midi_notes(camera3.handle_midi_note)
ProPresenter7.subscribe_to_midi_notes(camera4.handle_midi_note)
ProPresenter7.subscribe_to_midi_notes(camera5.handle_midi_note)

midi_note = {
    "port": None,
    "note": None,
    "mode": None,
    "velocity": None
}

atem = {
    "connected": False,
    "program": None,
    "preview": None,
    "inTransition": False
}

def get_render_data():
    return {
        "camera1": camera1.toJson(),
        "camera2": camera2.toJson(),
        "camera3": camera3.toJson(),
        "camera4": camera4.toJson(),
        "camera5": camera5.toJson(),
        "midi_note": midi_note,
        "atem": atem
    }


def log_midi_note(port, note, mode, velocity):
    midi_note["port"] = port
    midi_note["note"] = note
    midi_note["mode"] = mode
    midi_note["velocity"] = velocity


ProPresenter7.subscribe_to_midi_notes(log_midi_note)
