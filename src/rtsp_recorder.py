import os, signal
import cv2
import sys
import time
import rospy
from cv_bridge import CvBridge
from sensor_msgs.msg import Image, CameraInfo
# from camera_info_manager import *
# from threading import Thread
from time import sleep
import subprocess
from datetime import datetime as dt

SAVE_LOCATION = ''

def record(topics):
    # os.system('rosbag record camera_')
    topic_str = ' '.join(map(str, topics))
    print(topic_str)
    proc = subprocess.Popen(['rosbag', 'record', topic_str], shell=False)
    return proc, proc.pid


def stopRecord(proc):
   proc.terminate()


def addCamera(cam_data):
    # you should mess with the cam data to make it the correct format
    # <arg name="hostname" default='169.254.71.217' doc="hostname or IP of the rtsp camera" />
    # <arg name="username" default='administrator' doc="username for the rtsp camera" />
    # <arg name="password" default='smartbases' doc="password for the rtsp camera" />
    # <arg name="port" default="554" doc="port of the rtsp camera" />
    # <arg name="stream" default="defaultPrimary?mtu=1440&amp;streamType=m" doc="name of the video stream published by the rtsp camera" />
    proc = subprocess.Popen(['roslaunch', 'rtsp_camera rtsp_camera.launch', cam_data], shell=False)
    return proc, proc.pid


# def createStartSelect(repeat):
#     moment = dt.now()
#     year = moment.year
#     month = moment.month
#     day = moment.day
#     hour = moment.hour
#     minute = moment.minute
#     # One important thing to note is that in JavaScript 0 = Sunday, Python starts with 0 = Monday. Something that I ran into, front-end vs back-end -- stack overflow
#     wd = moment.weekday

#     start_date = str(year) + '-' + str(month) + '-' + str(day)
#     start_time = str(hour) + ':' + str(minute)
    
#     if repeat:
#         return 'SELECT * FROM recording_requests WHERE repeat=1, start_time={}, start_date<={}, weekday={}'.format(start_time, start_date, wd)
#     else:
#         return 'SELECT * FROM recording_requests WHERE repeat=0, start_time={}, start_date={}'.format(start_date, start_date)
    
def startSelectStatement():
    return '''SELECT * 
                FROM recordings 
                WHERE recordings.repeat = TRUE
                AND recordings.start_date <= CURRENT_DATE
                AND EXTRACT(DOW FROM CURRENT_DATE) = ANY (recordings.week_day)
                AND recordings.pid = -1
                AND recordings.start_time = date_trunc('minute', LOCALTIME(0))::time
                ; '''

# WHERE recordings.repeat = TRUE
#                     AND recordings.start_date <= CURRENT_DATE 
#                     AND EXTRACT(DOW FROM CURRENT_DATE) = ANY (recordings.week_day) 
#                     AND recordings.stop_date >= CURRENT_DATE 
#                    AND recordings.start_time = LOCALTIME(0)
                # AND recordings.pid = -1

def stopSelectStatement():
    return '''SELECT * 
                FROM recordings 
                WHERE recordings.start_date <= CURRENT_DATE 
                    AND EXTRACT(DOW FROM CURRENT_DATE) = ANY (recordings.week_day) 
                    AND recordings.stop_date >= CURRENT_DATE 
                    AND recordings.duration = (LOCALTIMESTAMP - recordings.last_started)
                ;'''

def check():
    print('check check. if you can see this, that is a good sign')