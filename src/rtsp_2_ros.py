#! /usr/bin/env python3

import os
import cv2
import sys
import time
import rospy
from cv_bridge import CvBridge
from sensor_msgs.msg import Image, CameraInfo, CompressedImage
from camera_info_manager import *
from threading import Thread
from time import sleep
import errlog

def do_math(resource, camera_name, camera_frame, image_topic, camera_info_topic):
    # initialize ROS node
    rospy.init_node(camera_name)
    errlog.progLog("doing math", level=0),
    image_topic += "/compressed"

    # open RTSP stream
    cap = cv2.VideoCapture(resource)
    if not cap.isOpened():
        errlog.progLog("Error opening resource `%s`. Please check." % resource, level=2)
        exit(0)
    errlog.progLog("Resource successfully opened")

    # create publishers
    # image_pub = rospy.Publisher(image_topic, Image, queue_size=1)
    image_pub = rospy.Publisher(image_topic, CompressedImage, queue_size=1)

    # initialize ROS_CV_Brideg
    ros_cv_bridge = CvBridge()
    

    # initialize variables
    errlog.progLog("Correctly opened resource, starting to publish feed???", level=0)
    rval, cv_image = cap.read()

    # process frames
    while True:
        if rval:
            # errlog.progLog("frames are being processed (maybe)", level=0)
            # get new frame
            rval, cv_image = cap.read()
        
            scale_percent = 50 # percent of original size
            width = int(cv_image.shape[1] * scale_percent / 100)
            height = int(cv_image.shape[0] * scale_percent / 100)
            dim = (width, height)
            # resize image
            cv_image = cv2.resize(cv_image, dim)
            # convert CV image to ROS message
            # image_msg = ros_cv_bridge.cv2_to_imgmsg(cv_image)
            image_msg = ros_cv_bridge.cv2_to_compressed_imgmsg(cv_image, dst_format='jpg')

            image_pub.publish( image_msg )
      
        

