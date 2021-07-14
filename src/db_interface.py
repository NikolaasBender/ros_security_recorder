import psycopg2 as pg
import time
import os
import rtsp_recorder as rtsp
import rospy
import sys
from multiprocessing import Process
import psycopg2.extras
import errlog

# read from db
def readDb(select_statement):
    errlog.progLog('reading from database', level=0)
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
        errlog.progLog(f"{rtsp.bcolors.FAIL}there was an error getting your things {error}{rtsp.bcolors.ENDC}", level=2)

    finally:
        errlog.progLog("end of db read", level=0)
        if(conn):
            # conn.commit()
            cursor.close()
            conn.close()
            return records


# save pid of job to db for later use
# used on process startup and process end
def insertPID(id, pid, table):
    errlog.progLog('inserting a pid for id', id, pid, level=0)
    insert_statement = 'UPDATE {} SET pid=%s'.format(table)
    if table == 'recordings':
        insert_statement += ', last_started=LOCALTIMESTAMP' 
    insert_statement += ' WHERE id=%s;'
    conn = None
    cursor = None
    try:
        conn = pg.connect(host="localhost",
                          database="smartbasesweb",
                          user="postgres",
                          password="smartbases")
        cursor = conn.cursor()
        cursor.execute(insert_statement, (pid, id,))
        errlog.progLog('updated', cursor.rowcount, level=0)
        conn.commit()

    except(Exception, pg.Error) as error:
        errlog.progLog(f"{rtsp.bcolors.FAIL}there was an error inserting the pids{error}{rtsp.bcolors.ENDC}", level=2)

    finally:
        errlog.progLog("end of db write", level=0)
        if(conn):
            cursor.close()
            conn.close()
            return 


# check that only the processes that should be running are
def checkRunning(records):
    errlog.progLog('checking things are running', level=0)
    failures = []
    for r in records:
        if r['pid'] == -1:
            failures.append(r)
        else:
            try:
                errlog.progLog('testing pid', r['pid'], level=0)
                os.kill(r['pid'], 0)
            except OSError:
                errlog.progLog('pid test failed', r['pid'], level=2)
                r['pid'] = -1
                failures.append(r)

    if len(failures) > 0:
        return False, failures
    else:
        return True, failures

def resetCameraPids():
    insert_statement = rtsp.camFirstRun()
    conn = None
    cursor = None
    try:
        conn = pg.connect(host="localhost",
                          database="smartbasesweb",
                          user="postgres",
                          password="smartbases")
        cursor = conn.cursor()
        cursor.execute(insert_statement,)
        errlog.progLog('updated', cursor.rowcount, level=0)
        conn.commit()

    except(Exception, pg.Error) as error:
        errlog.progLog(f"{rtsp.bcolors.FAIL}there was an error resetting the camera pids{error}{rtsp.bcolors.ENDC}", level=2)

    finally:
        errlog.progLog("end of db write", level=0)
        if(conn):
            cursor.close()
            conn.close()
            return 