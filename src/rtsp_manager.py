import psycopg2 as pg
import time
import os
import rtsp_recorder as rtsp

DATABASE_URL =

# sleep time in sec
T = 60

# this has the camera processes stored
CAMERAS = []

# this has the recording processes stored
RECORDINGS = {}


# read from db
def readDb(select_statement):
    conn = None
    cursor = None
    records = None
    try:
        conn = pg.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
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
def insertPID(id, pid):
    insert_statement = 'INSERT %s IN recordings WHERE id=%s'
    conn = None
    cursor = None
    try:
        conn = pg.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
        cursor.execute(insert_statement, [pid, id])

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
def cameraProcess():
    statement = ''
    camera_jobs = readDb(statement)
    stat, fails = checkRunning(camera_jobs)
    if not stat:
        for f in fails:
            if f.pid == -1:
                f.proc, f.pid = rtsp.record(f.topic)


# start necessary jobs
# stop certian jobs
def recordProcess():
    start_statement = "SELECT * FROM recordings WHERE start_day <= CURRENT_DATE AND EXTRACT(DOW FROM CURRENT_DATE) = ANY (week_day) AND stop_dat >= CURRENT_DATE AND start_time = to_char(LOCALTIME, 'HH:MI') ;"
    stop_statement = "SELECT * FROM recordings WHERE start_day <= CURRENT_DATE AND EXTRACT(DOW FROM CURRENT_DATE) = ANY (week_day) AND stop_dat >= CURRENT_DATE AND duration = to_char((LOCALTIMESTAMP - last_started), 'HH:MI') ;"
    # get jobs that need to be started
    start_jobs = readDb(start_statement)
    # get jobs that need to be stopped
    stop_jobs = readDb(stop_statement)
    # start jobs that need to start
    for sj in start_jobs:
        proc, pid = rtsp.record(sj.topic)
        RECORDINGS[pid] = {'id': sj[0],
                           'pid': pid,
                           'proc': proc,
                           'start_time': sj[7],
                           'stop_time': sj[7] + 
                           'topics': sj[9]}
        insertPID(sj[0], pid)
    # stop jobs that need to stop
    for stop in stop_jobs:
        rtsp.stopRecord(job_stop.proc)
        insertPID(sj[0], -1)


# keep everything running
def main():
    while True:
        time.sleep(T)
        cameraProcess()
        recordProcess()

# do the main loop
main()

    