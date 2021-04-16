#!/usr/bin/env python3

import time
import os
import rtsp_recorder as rtsp
import rospy
import sys
from multiprocessing import Process
import db_interface as db
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

# sleep time in sec
T = 60

# this has the camera processes stored
CAMERAS = {}

# this has the recording processes stored
RECORDINGS = {}

# connection string for our azure blob storage
az_connect = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_name = ''

# make sure all cameras are up and running
# good for also setting up new cameras
def cameraProcess(sleep_time):
    while True:
        statement = rtsp.cameraCheck()
        camera_jobs = db.readDb(statement)
        print(camera_jobs)
        stat, fails = db.checkRunning(camera_jobs)
        if not stat:
            for f in fails:
                if f['pid'] == -1:
                    proc, pid = rtsp.addCamera(f)
                    CAMERAS[f['topic_name']] = {
                        'id': f['id'],
                        'pid': pid,
                        'proc': proc,
                        'topic': f['topic_name']
                    }
                    db.insertPID(f['id'], pid, 'cameras')

        time.sleep(sleep_time)

# start necessary jobs
# stop certian jobs
def recordProcess(sleep_time):
    while True:
        print('running the record process')
        start_statement = rtsp.startSelectStatement()
        stop_statement = rtsp.stopSelectStatement()
        # get jobs that need to be started
        start_jobs = db.readDb(start_statement)
        print('jobs to start', start_jobs)
        # get jobs that need to be stopped
        stop_jobs = db.readDb(stop_statement)
        print('jobs to stop', stop_jobs)
        # start jobs that need to start
        if type(start_jobs) != type(None):
            for sj in start_jobs:
                proc, pid = rtsp.record(sj['camera_topics'])
                print('started a job', pid)
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
                    os.kill(stop['pid'], 0)
                    proc = RECORDINGS[stop['pid']]['proc']
                    rtsp.stopRecord(proc)
                    RECORDINGS.pop(stop['pid'])
                except OSError:
                    stop['pid'] = -1               
                db.insertPID(stop['id'], -1, 'recordings')
                # assert (len(RECORDINGS) < before), 'A recording was not deleted from the dict RECORDINGS.'
        # Find all non active bags and push to blob
        blobLoader()

        time.sleep(sleep_time)


def blobLoader():
    global_file_path = '~/catkin_ws/src/ros_security_recorder/src/'
    # double check this is correct for where the bags go
    bags = os.listdir(global_file_path)
    bags = [b for b in bags if '.bag.active' not in b and '.bag' in b]

    for b in bags:
        # Create a blob client using the local file name as the name for the blob
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=b)

        print("\nUploading to Azure Storage as blob:\n\t" + b)

        upload_file_path = os.path.join(global_file_path, b)

        # Upload the created file
        with open(upload_file_path, "rb") as data:
            blob_client.upload_blob(data)


# keep everything running
def main():
    rtsp.check()
    print('in main')

    c = Process(target=cameraProcess, args=(3600,))
    r = Process(target=recordProcess, args=(T,))
    c.start()
    r.start()
    c.join()
    r.join()

# do the main loop
main()

    