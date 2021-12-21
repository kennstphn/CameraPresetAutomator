import PyATEMMax
import application
import time

ip = '192.168.1.15'


def init_listener():
    switcher = PyATEMMax.ATEMMax()
    switcher.connect(ip)
    switcher.waitForConnection()
    while True:
        application.atem["program"] = int(str(switcher.programInput[0].videoSource).replace('input',''))
        application.atem["preview"] = int(str(switcher.previewInput[0].videoSource).replace('input',''))
        application.atem["inTransition"] = switcher.transition[0].inTransition
        application.atem["connected"] = switcher.connected
        time.sleep(0.016)  # more often than 1 / 60
