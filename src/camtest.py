import numpy as np
import cv2
import rospy
from cv_bridge import CvBridge
from sensor_msgs.msg import Image, CameraInfo, CompressedImage

camurl = "rtsp://administrator:smartbases@192.168.50.106:554/defaultPrimary?mtu=1440&streamType=m"

rospy.init_node('cam_tester')

cap = cv2.VideoCapture(camurl)
image_pub = rospy.Publisher('/desk_cam/compressed', CompressedImage, queue_size=1)
ros_cv_bridge = CvBridge()

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    print(ret)
    cv2.imshow('frame', frame)
    image_msg = ros_cv_bridge.cv2_to_compressed_imgmsg(frame, dst_format='jpg')
    image_pub.publish( image_msg )
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()


