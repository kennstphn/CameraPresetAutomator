import threading

import eel
import application
import time
import Switcher

eel.init("web")

switchListener = threading.Thread(target=Switcher.init_listener, name="Watch for changes in AtemSwitcher")
switchListener.setDaemon(True)
switchListener.start()


@eel.expose
def recall_camera(camera_number, preset_number):
    camera_list = {
        1: application.camera1,
        2: application.camera2,
        3: application.camera3,
        4: application.camera4,
        5: application.camera5
    }
    if camera_number not in camera_list:
        return
    camera_list[camera_number].handle_midi_note('manual', preset_number, 'ON', preset_number)


@eel.expose
def recall_camera_list(preset_number):
    application.camera1.handle_midi_note("manual", preset_number, "ON", preset_number)
    application.camera2.handle_midi_note("manual", preset_number, "ON", preset_number)
    application.camera3.handle_midi_note("manual", preset_number, "ON", preset_number)
    application.camera4.handle_midi_note("manual", preset_number, "ON", preset_number)
    application.camera5.handle_midi_note("manual", preset_number, "ON", preset_number)


def push_state():
    while True:
        eel.push_render_data(application.get_render_data())
        time.sleep(1 / 60)


data_bridge = threading.Thread(target=push_state, name='Hello world')
data_bridge.setDaemon(True)
data_bridge.start()

eel.start("index.html",
          mode='default',
          host='localhost',
          port=27000,  # default is 8000
          block=True,  # block on eel.start
          size=(700, 480),  # application window size
          position=(0, 0),
          disable_cache=True,
          # close_callback=, #  callable function to clean up or store stuff
          cmdline_args=[
              # '--browser-startup-dialog',
              # '--incognito',
              # '--no-experiments'
          ]
          )
