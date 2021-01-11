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
RECORDINGS = []

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

# start new recordings
# def runner(requests):
#     for r in requests:
#         r.proc, r.pid = rtsp.record(r.topic)

# kill processes that need to end
def johnWick(requests):
    for r in requests:
        rtsp.stopRecord(r.proc)


def cameraProcess():
    statement = ''
    camera_jobs = readDb(statement)
    stat, fails = checkRunning(camera_jobs)
    if not stat:
        for f in fails:
            if f.pid == -1:
                f.proc, f.pid = rtsp.record(f.topic)


def recordProcess():
    start_statement = ''
    stop_statement = ''
    start_jobs = readDb(start_statement)
    stop_jobs = readDb(stop_statement)
    start_stat, start_fails = checkRunning(start_jobs)
    stop_stat, stop_fails = checkRunning(stop_jobs)
    if not start_stat:
        for f in start_fails:
            if f.pid == -1:
                f.proc, f.pid = rtsp.record(f.topic)
    if not stop_stat:
        for f in stop_fails:
            if f.pid == -1:
                f.proc, f.pid = rtsp.record(f.topic)

def main():
    while True:
        time.sleep(T)
        cameraProcess()
        recordProcess()

# do the main loop
main()

    