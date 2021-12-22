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
    camera = application.get_camera(camera_number)
    if camera is None:
        return
    camera.handle_midi_note('manual', preset_number, 'ON', preset_number)


@eel.expose
def recall_camera_list(preset_number):
    application.camera1.handle_midi_note("manual", preset_number, "ON", preset_number)
    application.camera2.handle_midi_note("manual", preset_number, "ON", preset_number)
    application.camera3.handle_midi_note("manual", preset_number, "ON", preset_number)
    application.camera4.handle_midi_note("manual", preset_number, "ON", preset_number)
    application.camera5.handle_midi_note("manual", preset_number, "ON", preset_number)


@eel.expose
def go_to_position(camera_number, ptz_triple):
    camera = application.get_camera(camera_number)
    if camera is None:
        raise Exception('Camera not found')
    thread = threading.Thread(target=camera.go_to_position, name="Camera ptz movement " + str(camera.number),
                              kwargs={"preset_position": ptz_triple})
    thread.setDaemon(True)
    thread.start()


@eel.expose
def load_preset_list(ptz_triple_list_list):
    thread1 = application.camera1.make_load_preset_thread(ptz_triple_list_list[0])
    thread2 = application.camera2.make_load_preset_thread(ptz_triple_list_list[1])
    thread3 = application.camera3.make_load_preset_thread(ptz_triple_list_list[2])
    thread4 = application.camera4.make_load_preset_thread(ptz_triple_list_list[3])
    thread5 = application.camera5.make_load_preset_thread(ptz_triple_list_list[4])

    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    thread5.start()

    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()
    thread5.join()

    return "OK"


@eel.expose
def store_current_position_as_preset(i):
    application.camera1.store_preset(i)
    application.camera2.store_preset(i)
    application.camera3.store_preset(i)
    application.camera4.store_preset(i)
    application.camera5.store_preset(i)
    return "OK"


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
