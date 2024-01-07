# This file contains class for the drive stepper motors

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)
import time
import threading
from typing import List

n_motors = 2
dir = [True, False]
slack = 0.001
del_max = 0.001
del_min = 2e-6

# Class for two stepper motors
class motors:

    def __init__(self, en_pins: List[int], dir_pins: List[int], step_pins: List[int]):
        # Save the pins numbers
        self._en_pins = en_pins
        self._dir_pins = dir_pins
        self._step_pins = step_pins

        # Initialize GPIO
        for i in range(n_motors):
            GPIO.setup(self._step_pins[i], GPIO.OUT)
            GPIO.setup(self._dir_pins[i], GPIO.OUT)
            GPIO.setup(self._en_pins[i], GPIO.OUT)

        # Set initially to stop, delay to 1 sec and direction to 1 = forward
        self._run = [False, False]
        self._delay = [1, 1]
        self._direction = [1, 1]
        self._drive_thread = [1, 1]
        self._active = False

        # Enable the motors
        for i in range(n_motors):
            GPIO.output(self._en_pins[i], GPIO.LOW)


    def map_velocity(self, input: List[float]):
        '''
            Function for mapping velocity (including direction) from [-1, 1] to delay between step commands
        '''

        if(len(input) != n_motors):
            raise ValueError('Incorrect number of inputs in the list')

        for i in range(n_motors):
            if(abs(input[i]) > slack):
                # Determine direction
                if(input[i] < 0):
                    self._direction[i] = 0
                else:
                    self._direction[i] = 1

                # Determine delay
                self._run[i] = True
                self._delay[i] = (del_min-del_max)*abs(input[i]) + del_max # Map from [0,1] to [del_max, del_min]
            else:
                self._run[i] = False

    def set_enable(self, input: List[bool]):
        '''
            Function for setting the state of the enable pins --> Allows freewheeling
        '''

        if(len(input) != n_motors):
            raise ValueError('Incorrect number of inputs in the list')

        for i in range(n_motors):
            GPIO.output(self._en_pins[i], input[i])


    def activate(self):
        self._active = True
        for i in range(n_motors):
            self._drive_thread[i] = threading.Thread(target=self._run_motor, args=(i,))
            self._drive_thread[i].start()


    def deactivate(self):
        if(self._active):
            self._active = False
            for i in range(n_motors):
                self._drive_thread[i].join()
            GPIO.cleanup()



    def _run_motor(self, num: int):
        '''
            Function that gives the motor the drive signal, needs to be run in separate thread
        '''
                
        while(self._active):

            # Set direction
            GPIO.output(self._dir_pins[num], (dir[num] ^ self._direction[num]))

            # Give the step signal
            if(self._run[num]):
                GPIO.output(self._step_pins[num], GPIO.LOW)
                time.sleep(self._delay[num])
                GPIO.output(self._step_pins[num], GPIO.HIGH)
                time.sleep(self._delay[num])
            else:
                time.sleep(del_max)

                

