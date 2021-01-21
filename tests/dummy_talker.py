import rospy
from std_msgs.msg import String
from multiprocessing import Pool

def talker(num):
    pub = rospy.Publisher('chatter'+str(num), String, queue_size=10)
    rate = rospy.Rate(5) # 10hz
    while not rospy.is_shutdown():
        hello_str = "hello world {} from talker {}".format(rospy.get_time(), num)
        rospy.loginfo(hello_str)
        pub.publish(hello_str)
        rate.sleep()

if __name__ == '__main__':
    ids = [0, 1, 2, 3]
    rospy.init_node('talker', anonymous=True)
    try:
        with Pool(4) as p:
            p.map(talker, ids)
    except rospy.ROSInterruptException:
        pass