import os, signal
import cv2
import sys
import time
import rospy
from cv_bridge import CvBridge
from sensor_msgs.msg import Image, CameraInfo
from camera_info_manager import *
from threading import Thread
from time import sleep
import subprocess

def record(topics):
    # os.system('rosbag record camera_')
    proc = subprocess.Popen(['rosbag', 'redord', topics], shell=False)
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