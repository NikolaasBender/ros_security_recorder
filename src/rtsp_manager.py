#!/usr/bin/env python3

import psycopg2 as pg
import time
import os
import rtsp_recorder as rtsp
import rospy
import sys
from multiprocessing import Process

# DATABASE_INFO = 
#     "localhost",
#     "smartbaseweb",
#     "postgres",
#     "smartbases")

# sleep time in sec
T = 60

# this has the camera processes stored
CAMERAS = []

# this has the recording processes stored
RECORDINGS = {}


# read from db
def readDb(select_statement):
    print('reading from database')
    conn = None
    cursor = None
    records = None
    try:
        conn = pg.connect(host="localhost",
                          database="smartbasesweb",
                          user="postgres",
                          password="smartbases")
        cursor = conn.cursor(cursor_factory=pg.extras.DictCursor)
        selector = select_statement
        cursor.execute(selector)
        records = cursor.fetchall()

    except(Exception, pg.Error) as error:
        print("there was an error getting your things", error)

    finally:
        print("end of db read")
        if(conn):
            cursor.close()
            conn.close()
            return records


# save pid of job to db for later use
# used on process startup and process end
def insertPID(id, pid, table):
    print('inserting a pid for id', id, pid)
    insert_statement = 'UPDATE recordings SET pid=%s, last_started=LOCALTIMESTAMP WHERE id=%s;'
    conn = None
    cursor = None
    try:
        conn = pg.connect(host="localhost",
                          database="smartbasesweb",
                          user="postgres",
                          password="smartbases")
        cursor = conn.cursor()
        cursor.execute(insert_statement, (pid, id,))
        print('updated', cursor.rowcount)
        conn.commit()

    except(Exception, pg.Error) as error:
        print("there was an error inserting the pid", error)

    finally:
        print("end of db write")
        if(conn):
            cursor.close()
            conn.close()
            return 


# check that only the processes that should be running are
def checkRunning(records):
    print('checking things are running')
    failures = []
    for r in records:
        # Sending signal 0 to a pid will raise an OSError exception if the pid is not running, and do nothing otherwise.
        try:
            os.kill(r.pid, 0)
        except OSError:
            r.pid = -1
            failures.append(r)

    if len(failures) > 0:
        return False, failures
    else:
        return True, failures


# make sure all cameras are up and running
# good for also setting up new cameras
def cameraProcess(sleep_time):
    while True:
        statement = rtsp.cameraCheck()
        camera_jobs = readDb(statement)
        stat, fails = checkRunning(camera_jobs)
        if not stat:
            for f in fails:
                if f.pid == -1:
                    f.proc, f.pid = rtsp.record(f.topic)
                
        time.sleep(sleep_time)

# start necessary jobs
# stop certian jobs
def recordProcess(sleep_time):
    while True:
        print('running the record process')
        start_statement = rtsp.startSelectStatement()
        stop_statement = rtsp.stopSelectStatement()
        # get jobs that need to be started
        start_jobs = readDb(start_statement)
        print('jobs to start', start_jobs)
        # get jobs that need to be stopped
        stop_jobs = readDb(stop_statement)
        print(stop_jobs)
        # start jobs that need to start
        if type(start_jobs) != type(None):
            for sj in start_jobs:
                proc, pid, file_name = rtsp.record(sj['topics'])
                print('started a job', pid)
                RECORDINGS[pid] = {'id': sj['id'],
                                'pid': pid,
                                'proc': proc,
                                'start_time': sj['start_time'],
                                'stop_time': sj['stop_time'],
                                'topics': sj['topics'],
                                'file_name': file_name}
                insertPID(sj['id'], pid, 'recordings')
        # stop jobs that need to stop
        for stop in stop_jobs:
            rtsp.stopRecord(stop.proc, RECORDINGS[stop.pid]['file_name'])
            insertPID(sj['id'], -1)
        time.sleep(sleep_time)


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

    