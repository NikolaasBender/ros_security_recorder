import psycopg2 as pg
import time
import os
import rtsp_recorder as rtsp
import rospy
import sys
from multiprocessing import Process
import psycopg2.extras

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
            conn.commit()
            # cursor.close()
            # conn.close()
            return records


# save pid of job to db for later use
# used on process startup and process end
def insertPID(id, pid, table):
    print('inserting a pid for id', id, pid)
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
        if r['pid'] == -1:
            failures.append(r)
        else:
            try:
                os.kill(r['pid'], 0)
            except OSError:
                r['pid'] = -1
                failures.append(r)

    if len(failures) > 0:
        return False, failures
    else:
        return True, failures