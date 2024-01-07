# This file contains some utility functions for checking network, etc.

import http.client as httplib
import os
import requests
from typing import Dict

def has_internet() -> bool:
    '''
        A function for checking whether the Pi has internet connection
    '''
    conn = httplib.HTTPSConnection("8.8.8.8", timeout=5)
    try:
        conn.request("HEAD", "/")
        return True
    except Exception:
        return False
    finally:
        conn.close()


def read_credentials(filename = os.path.dirname(__file__) + '/secrets.dat'):
    '''
        A function for reading the TG bot credentials from a file
    '''
    credentials = {}
    f = open(filename, 'r')
    for line in f.readlines():
        if(len(line.replace(' ', '')) > 0):
            pts = line.replace(' ','').replace('\n', '').split(';')
            credentials[pts[0]] = pts[1]

    f.close()

    return credentials


def announce_ip(local_stream = True, port = '8082', yt_address = ''):
    '''
        A simple method for telling the ip address and video stream address of the Pi
    '''

    data = read_credentials()

    ip = os.popen('hostname -I').read().split(' ')[0].rstrip()
    message = 'Hello there!\n\nToday my IP address is: ' + ip  
    if(local_stream):
        message = message + '\n\nYou can access the video stream from http://' + ip + ':' + port
    else:
        message = message + '\n\nYou can access the video stream from ' + data['yt_address']

    url = f"https://api.telegram.org/bot{data['TOKEN']}/sendMessage?chat_id={data['ID']}&text={message}"
    requests.get(url).json()



def map_dpad(input: Dict[str, int], cam):
    '''
        A method for mapping controller class output dict to camera movements
    '''

    if(input['DP_up']):
        cam.change_tilt(5)
    elif(input['DP_down']):
        cam.change_tilt(-5)
    elif(input['DP_right']):
        cam.change_pan(-15)
    elif(input['DP_left']):
        cam.change_pan(15)
    else:
        pass
