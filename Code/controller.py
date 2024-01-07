# This file contains class for the gamepad controller

import RPi.GPIO as GPIO
import evdev
import time
from typing import List, Dict


# Class for gamepad controller
class gamepad:

    def __init__(self):
        self._dev_path = ''
        self._is_connected = False


    def connect(self, name: str, abs_axes: Dict[str, int], dpad: Dict[str, int], buttons: Dict[str, int], wait = True, timeout = 40):
        '''
            Connect to controller (or device) with specific name and with specific axis mapping
            and button mapping
            If the device is not found after timeout an IOerror is raised
        '''
        t_start = time.time()
        found = False
        while(not found and time.time()-t_start < timeout):
            dev_list = evdev.list_devices()
            self._dev_path = ''
            for dev in dev_list:
                dev_name = evdev.InputDevice(dev).name
                if(name.lower() in dev_name.lower()):
                    found = True
                    self._dev_path = dev
                    break
            time.sleep(0.5)
        
        if(not found):
            raise IOError('No gamepad controller with name "' + name + '" found')
        else:
            self._dev = evdev.InputDevice(self._dev_path)
            # ToDo: Add safety check that the given controller really has these axes
            self._axes = abs_axes
            self._dpad = dpad
            self._btns = buttons
            self._is_connected = True
        

    def check_connection(self):
        '''
            Check whether the gamepad controller is available
        '''
        dev_list = evdev.list_devices()
        self._is_connected = False
        for dev in dev_list:
            try:
                dev_name = evdev.InputDevice(dev).name
            except FileNotFoundError:
                pass
            if(self._dev.name.lower() ==  dev_name.lower()):
                self._is_connected = True

        return self._is_connected 


    def read_axes(self, ax_list: List[str]):
        '''
            Read the given absolute axes from the gamepad and map the values to [-1, 1]
        '''
        if(not self._is_connected):
            raise IOError('No gamepad controller with name is connected')

        values = []
        for ax in ax_list:
            if(ax in list(self._axes.keys())):
                values.append((self._dev.absinfo(self._axes[ax]).value - (self._dev.absinfo(self._axes[ax]).max + 1)/2)/((self._dev.absinfo(self._axes[ax]).max + 1)/2))
            else:
                raise ValueError('Controller does not have axis ' + ax)
            
        return values


    def read_dpad(self):
        '''
            Read the dpad and return a dict
        '''
        if(not self._is_connected):
            raise IOError('No gamepad controller with name is connected')

        values = {'DP_up': 0, 'DP_down': 0, 'DP_right': 0, 'DP_left': 0}
        for ax in list(self._dpad.keys()):
            if('X' in ax):
                val = self._dev.absinfo(self._dpad[ax]).value
                if(val == 1):
                    values['DP_right'] = 1
                elif(val == -1):
                    values['DP_left'] = 1
            else:
                val = self._dev.absinfo(self._dpad[ax]).value
                if(val == 1):
                    values['DP_down'] = 1
                elif(val == -1):
                    values['DP_up'] = 1
            
        return values


    def read_buttons(self, bt_list: List[int]):
        '''
            Read the given buttons and return their state as a list of booleans
        '''
        if(not self._is_connected):
            raise IOError('No gamepad controller with name is connected')

        values = []
        active = self._dev.active_keys()
        for bt in bt_list:
            if(bt in list(self._btns.keys())):
                values.append(self._btns[bt] in active)
            else:
                raise ValueError('Controller does not have button ' + bt)
        
        return values
