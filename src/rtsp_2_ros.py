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

# this reads the rtsp stream and converts it to ros messages
def do_math(resource, camera_name, camera_frame, image_topic, camera_info_topic):
    sleep(60)
    # initialize ROS node
    rospy.init_node(camera_name)
    errlog.progLog("starting a camera", level=0),
    image_topic += "/compressed"

    # open RTSP stream
    cap = cv2.VideoCapture(resource)
    while not cap.isOpened():
        errlog.progLog("Error opening resource `%s`. Please check." % resource, level=2)
        cap = cv2.VideoCapture(resource)
        sleep(30)
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
            rval = None
            cv_image = None
            try: 
                rval, cv_image = cap.read()
                # errlog.progLog("Success reading resource `%s`" % resource, level=0)
            except:
                errlog.progLog("Error reading resource `%s`. Please check." % resource, level=2)
                
            if type(cv_image) is not type(None): 
                try:
                    scale_percent = 50 # percent of original size
                    width = int(cv_image.shape[1] * scale_percent / 100)
                    height = int(cv_image.shape[0] * scale_percent / 100)
                    dim = (width, height)
                    # resize image
                    cv_image = cv2.resize(cv_image, dim)
                
                except:
                    errlog.progLog("Error resizing images %s" % resource, level=2)
                
                try:
                    # convert CV image to ROS message
                    # image_msg = ros_cv_bridge.cv2_to_imgmsg(cv_image)
                    image_msg = ros_cv_bridge.cv2_to_compressed_imgmsg(cv_image, dst_format='jpg')
                    image_pub.publish( image_msg )
                except:
                    errlog.progLog("Error publishing images %s" % resource, level=2)
            else:
                errlog.progLog("cv image is still none %s" % resource, level=2)
                
            
        else:
            errlog.progLog("no frame from " + camaera_name, level=2)
      
    errlog.progLog("leaving conversion " + camaera_name, level=2)

