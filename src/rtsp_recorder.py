import os
import cv2
import sys
import time
import rospy
from cv_bridge import CvBridge
from sensor_msgs.msg import Image, CameraInfo
from camera_info_manager import *
from threading import Thread
from time import sleep

def record(resource, location, time_end):
    os.exec('rosbag record camera_')

    