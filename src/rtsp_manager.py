#!/usr/bin/env python3

import time
import os, signal
import rospy
import sys
from multiprocessing import Process, Pool
import db_interface as db
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, BlobSasPermissions
import errlog
import rtsp_recorder as rtsp

# sleep time in sec
T = 60

# this has the camera processes stored
CAMERAS = {}

# this has the recording processes stored
RECORDINGS = {}

AZURE_UPLOAD = True

# connection string for our azure blob storage
# ENV didn't work
# az_connect = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

f = open('connect.ourkey', 'r')
sas_url = f.read()
blob_service_client = ContainerClient.from_container_url(sas_url)

#blob_service_client = BlobServiceClient.from_connection_string("key")
container_name = 'smartbases'

# make sure all cameras are up and running
# good for also setting up new cameras
def cameraProcess(sleep_time):
    while True:
        statement = rtsp.cameraCheck()
        camera_jobs = [db.readDb(statement)]
        errlog.progLog(camera_jobs, level=0)
        # stat, fails = db.checkRunning(camera_jobs)
        # errlog.progLog(fails, level=1)
        errlog.progLog('new camera processes to start', level=0)
        with Pool(5) as p:
            p.map(rtsp.addCamera, *camera_jobs)
                # proc, pid = rtsp.addCamera(f)
                # errlog.progLog('pid response from add camera:', pid, level=0)
                # CAMERAS[f['topic_name']] = {
                #     'id': f['id'],
                #     'pid': pid,
                #     'proc': proc,
                #     'topic': f['topic_name']
                # }
                # db.insertPID(f['id'], pid, 'cameras')

        time.sleep(sleep_time)

# start necessary jobs
# stop certian jobs
def recordProcess(sleep_time):
    while True:
        errlog.progLog('running the record process', level=0)
        start_statement = rtsp.startSelectStatement()
        stop_statement = rtsp.stopSelectStatement()
        # get jobs that need to be started
        start_jobs = db.readDb(start_statement)
        errlog.progLog('jobs to start', start_jobs, level=0)
        # get jobs that need to be stopped
        stop_jobs = db.readDb(stop_statement)
        errlog.progLog('jobs to stop', stop_jobs, level=0)
        # start jobs that need to start
        if type(start_jobs) != type(None):
            for sj in start_jobs:
                proc, pid = rtsp.record(sj['camera_topics'])
                errlog.progLog('started a job', pid, level=0)
                RECORDINGS[pid] = {'id': sj['id'],
                                'pid': pid,
                                'proc': proc,
                                'start_time': sj['start_time'],
                                'topics': sj['camera_topics']}
                db.insertPID(sj['id'], pid, 'recordings')

        # stop jobs that need to stop
        if type(stop_jobs) != type(None):
            for stop in stop_jobs:
                # before = len(RECORDINGS)
                try:
                    # os.kill(stop['pid'], 2)
                    os.kill(stop['pid'], signal.SIGINT)
                    proc = RECORDINGS[stop['pid']]['proc']
                    # rtsp.stopRecord(proc)
                    RECORDINGS.pop(stop['pid'])
                except OSError:
                    stop['pid'] = -1               
                db.insertPID(stop['id'], -1, 'recordings')
                # assert (len(RECORDINGS) < before), 'A recording was not deleted from the dict RECORDINGS.'
        # Find all non active bags and push to blob
        # blobLoader()

        time.sleep(sleep_time)


def blobLoader():
    errlog.progLog('blob loader active', level=0)
    # global_file_path = os.curdir()
    # double check this is correct for where the bags go
    # bags = os.listdir(global_file_path)
    bags = os.listdir()
    bags = [b for b in bags if '.bag.active' not in b and '.bag' in b]
    
    errlog.progLog("bags:", bags, level=0)

    for b in bags:

        if not AZURE_UPLOAD:
            errlog.progLog("\nsaving bag to drive:\n\t" + b, level=0)
            target_folder = "media/shack_nuc/smartbases"
            target_file = b
            errlog.progLog("target file: " + target_file, level=0)
            if os.path.exists(str(target_file)):
                shutil.move(target_file, target_folder)
            else:
                errlog.progLog("\ncan not access drive:\n\t" + b, level=2)
            errlog.progLog("\ndone saving bag to drive:\n\t" + b, level=0)


        else:
            # Create a blob client using the local file name as the name for the blob
            # blob_client = blob_service_client.get_blob_client(container=container_name, blob=b)
            blob_client = blob_service_client.get_blob_client(blob=b)
            errlog.progLog("\nUploading to Azure Storage as blob:\n\t" + b, level=0)
            global_file_path = '~/catkin_ws/src/ros_security_recorder/src/'
            upload_file_path = os.path.join(global_file_path, b)

            # Upload the created file
            try:
                with open(upload_file_path, "rb") as data:
                    blob_client.upload_blob(data)
                
                errlog.progLog('upload complete', level=1)

                if os.path.exists(upload_file_path):
                    os.remove(upload_file_path)
                else:
                    errlog.progLog("file delete error name: ", upload_file_path, level=2)
            except err:
                errlog.progLog('error uploading bag name: ', upload_file_path, err, level=2)


    errlog.progLog('end blob loader', level=0)


def blobSpinner(sleep_time):
    while True:
        blobLoader()
        time.sleep(sleep_time)

# keep everything running
def main():
    # rospy.init_node('rtsp_manager')
    
    errlog.progLog('in main', level=0)

    c = Process(target=cameraProcess, args=(600,))
    r = Process(target=recordProcess, args=(T,))
    u = Process(target=blobSpinner, args=(T,))
    c.start()
    r.start()
    u.start()
    c.join()
    r.join()
    u.join()
    
    rospy.spin()

# do the main loop
main()

    
