# This file contains class for the Pi camera and its pan/tilt servos

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
import time
import multiprocessing
import server

# Class for the raspberry Pi camera with the pan&tilt axes
class camera:

    def __init__(self, tilt_pin: int, pan_pin: int):

        self._streaming = False

        # Servo control variables
        self._axes = [0,1]
        self._pins = (tilt_pin, pan_pin)
        self._curr_angles = [90, 90]
        self._home_angles = (90, 90)
        self._lims = [(40, 130), (20, 160)]
        self._pwm = []

        # Init pwm
        for i in self._axes:
            GPIO.setup(self._pins[i], GPIO.OUT)
            self._pwm.append(GPIO.PWM(self._pins[i], 50))
            self._pwm[i].start(0)

        #self.home()


    def change_tilt(self, d_angle: int):
        '''
            Change the tilt angle by d_angle sized step
        '''
        self._set_angle(0, self._curr_angles[0] + d_angle)


    def change_pan(self, d_angle: int):
        '''
            Change the pan angle by d_angle sized step
        '''
        self._set_angle(1, self._curr_angles[1] + d_angle)
        

    def home(self):
        '''
            Set both pan and tilt to the home position (pointing forward)
        '''
        self._set_angle(0, self._home_angles[0])
        self._set_angle(1, self._home_angles[1])


    def _set_angle(self, axis: int, angle: int):
        '''
            Set angle for the given axis (0 = tilt, 1 = pan), if the angle is inside the limits
        '''
        if(axis in self._axes):
            self._curr_angles[axis] = min(max(angle, self._lims[axis][0]), self._lims[axis][1])
            duty = self._curr_angles[axis] / 18 + 2
            GPIO.output(self._pins[axis], True)
            self._pwm[axis].ChangeDutyCycle(duty)
            time.sleep(0.2)
            GPIO.output(self._pins[axis], False)
            self._pwm[axis].ChangeDutyCycle(0)


    def start_stream(self):
        '''
            Start the video streaming to the web page
        '''
        self._stream_process = multiprocessing.Process(target=server.main)
        self._streaming = True
        self._stream_process.start()
        

    def stop_stream(self):
        '''
            Stop the video stream
        '''
        if(self._streaming):
            self._streaming = False
            self._stream_process.kill()
            GPIO.cleanup()

