import controller
import stepper
import camera
import utils
import time

axes = {'RX': 3,
        'RY': 4,
        'LX': 0,
        'LY': 1}

dpad = {'DPX': 16,
        'DPY': 17}

buttons = {'RS': 309, 'LS': 308, 'SEL': 310, 'A': 305}

en = [21, 1]
step = [16, 8]
dir = [20, 7]


gp = controller.gamepad()
gp.connect('8bitdo', axes, dpad, buttons)

mot = stepper.motors(en, dir, step)
cam = camera.camera(12,13)

mot.activate()
mot.map_velocity([0, 0])

if(utils.has_internet()):
    utils.announce_ip()
    cam.start_stream()

while gp.check_connection():
    vels = gp.read_axes(['LY', 'RY'])
    mot.set_enable(gp.read_buttons(['LS', 'RS']))
    mot.map_velocity(vels)
    
    utils.map_dpad(gp.read_dpad(), cam)
    
    if(gp.read_buttons(['A'])[0]):
        cam.home()

    if(gp.read_buttons(['SEL'])[0]):
        break
    
mot.deactivate()
cam.stop_stream()
