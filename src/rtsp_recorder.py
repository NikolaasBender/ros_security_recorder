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
import re

SAVE_LOCATION = ''

def record(topics):
    # os.system('rosbag record camera_')
    print('topic string', topics)
    bag_name = 'please_change_me.bag'
    proc = subprocess.Popen(['rosbag', 'record', '-O', bag_name, *topics], shell=False)
    return proc, proc.pid, bag_name


def stopRecord(proc, file_name):
   proc.terminate()


def addCamera(cam_data):
    # you should mess with the cam data to make it the correct format
    # <arg name="hostname" default='169.254.71.217' doc="hostname or IP of the rtsp camera" />
    # <arg name="username" default='administrator' doc="username for the rtsp camera" />
    # <arg name="password" default='smartbases' doc="password for the rtsp camera" />
    # <arg name="port" default="554" doc="port of the rtsp camera" />
    # <arg name="stream" default="defaultPrimary?mtu=1440&amp;streamType=m" doc="name of the video stream published by the rtsp camera" />
    # cli arg like this hoge:=my_value
    print(cam_data['hostname'])
    hostname = cam_data['hostname'][1: len(cam_data['hostname'])-1]
    print(hostname)
    proc = subprocess.Popen(['roslaunch', 'rtsp_ros_driver', 'rtsp_camera.launch', 'hostname:='+hostname, 'username:='+cam_data['username'], 'password:='+cam_data['password'] ], shell=False)
    return proc, proc.pid


def startSelectStatement():
    return '''SELECT *
                FROM recordings 
                WHERE (recordings.repeat = TRUE
                        AND recordings.start_date <= CURRENT_DATE
                        AND EXTRACT(DOW FROM CURRENT_DATE) = ANY (recordings.week_day)
                        AND recordings.pid = -1
                        AND recordings.start_time = date_trunc('minute', LOCALTIME(0))::time) 
                        OR (recordings.repeat = FALSE
                        AND recordings.start_date = CURRENT_DATE
                        AND recordings.pid = -1
                        AND recordings.start_time = date_trunc('minute', LOCALTIME(0))::time)
                     ; '''


def stopSelectStatement():
    return '''SELECT * 
                FROM recordings 
                WHERE recordings.start_date <= CURRENT_DATE 
                    AND recordings.pid != -1
                    AND recordings.duration = date_trunc('minute', (LOCALTIMESTAMP - recordings.last_started))
                ;'''

def cameraCheck():
    return '''SELECT * 
                FROM cameras
                ;'''

def check():
    print('check check. if you can see this, that is a good sign')
