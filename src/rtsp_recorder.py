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
import errlog
import db_interface as db
import rtsp_2_ros

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

SAVE_LOCATION = ''

def record(topics):
    # os.system('rosbag record camera_')
    # try:
    #     topics = validateTopics(topics)
    # except:
    #     errlog.progLog('error validating topics', level=2)
    topics = validateTopics(topics)
    errlog.progLog('topic string ', topics, level=0)
    # bag_name = 'please_change_me.bag'
    # proc = subprocess.Popen(['rosbag', 'record', '-O', bag_name, *topics], shell=False)
    proc = subprocess.Popen(['rosbag', 'record', *topics], shell=False)
    return proc, proc.pid


def validateTopics(topics):
    # get the topics from the cameras table
    # db_topics = db.readDb('select topic_name from cameras')
    # dbt = [t['topic_name'] for t in db_topics]
    # get the topics alive in ros
    # ros_topics = rospy.get_published_topics()
    # ros_topics = list(set([rt[0].split('/')[1] for rt in ros_topics if rt != '/rosout' or rt != '/rosout_agg']))
    # errlog.progLog('db topics: ', dbt, ' ros topics: ', ros_topics, level=1)
    # if dbt.sort() != ros_topics.sort():
    #     errlog.progLog('error asserting that active ros topics are the same as in the db', level=2)
        # raise 
    # if set(topics).issubset(set(ros_topics)) == False:
    #     errlog.progLog('error asserting that requested topics exist as active ros topics', level=2)
        # return None
    # if set(topics).issubset(set(dbt)) == False:
    #     errlog.progLog('error asserting that requested topics exist in the database', level=2)
        # return None
    # everything checks out, return good topics
    topics = [t+'/compressed' for t in topics]
    return topics
    

def stopRecord(proc):
   proc.terminate()


def addCamera(cam_data):
    # you should mess with the cam data to make it the correct format
    # <arg name="hostname" default='169.254.71.217' doc="hostname or IP of the rtsp camera" />
    # <arg name="username" default='administrator' doc="username for the rtsp camera" />
    # <arg name="password" default='smartbases' doc="password for the rtsp camera" />
    # <arg name="port" default="554" doc="port of the rtsp camera" />
    # <arg name="stream" default="defaultPrimary?mtu=1440&amp;streamType=m" doc="name of the video stream published by the rtsp camera" />
    # cli arg like this hoge:=my_value
    # errlog.progLog('hostname to use:', cam_data['hostname'], level=0)
    # proc = subprocess.Popen(['roslaunch', 'rtsp_ros_driver', 'rtsp_camera.launch', 'hostname:='+hostname, 'username:='+cam_data['username'], 'password:='+cam_data['password'], 'camera_name:='+cam_data['topic_name'], ], shell=False)
    # errlog.progLog('newly started camera pid', proc.pid)
    # return proc, proc.pid

    urlTemp = "rtsp://administrator:smartbases@192.168.50.106:554/defaultPrimary?mtu=1440&streamType=m"
    # resource=f"rtsp://{cam_data['username']}:{cam_data['password']}@{cam_data['hostname']}:{cam_data['port']}/{cam_data['stream']}"


    resource=f"rtsp://{cam_data['username']}:{cam_data['password']}@{cam_data['hostname']}:{cam_data['port']}/defaultPrimary?mtu=1440&streamType=m"

    if(urlTemp == resource):
        errlog.progLog('oh my ;-) your hostname and password are valid for the test cam')

    rtsp_2_ros.do_math(resource, cam_data['topic_name'], "i_hope_nobody_sees_this",  cam_data['topic_name'], '/camera_info')
    


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

def camFirstRun():
    return '''UPDATE cameras SET pid = -1 WHERE pid != -1;'''

def check():
    errlog.progLog('check check. if you can see this, that is a good sign', level=1)
