CREATE TABLE cameras(
    id SERIAL PRIMARY KEY,
    pid INT DEFAULT -1,
    topic_name TEXT NOT NULL,
    hostname TEXT NOT NULL, 
    username TEXT DEFAULT 'administrator',
    password TEXT DEFAULT 'smartbases',
    port TEXT DEFAULT '554',
    stream TEXT DEFAULT 'defaultPrimary?mtu=1440&amp;streamType=m'
)

-- rtsp://169.254.71.217/defaultPrimary?mtu=1440&streamType=m
-- <arg name="hostname" default='169.254.71.217' doc="hostname or IP of the rtsp camera" />
-- <arg name="username" default='administrator' doc="username for the rtsp camera" />
-- <arg name="password" default='smartbases' doc="password for the rtsp camera" />
-- <arg name="port" default="554" doc="port of the rtsp camera" />
-- <arg name="stream" default="defaultPrimary?mtu=1440&amp;streamType=m" doc="name of the video stream published by the rtsp camera" />