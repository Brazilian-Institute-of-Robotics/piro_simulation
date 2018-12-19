#!/usr/bin/env python
import rospy
from std_msgs.msg  import Float64
from geometry_msgs.msg import Twist
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

class arm_mimic_control():

    def __init__(self):
        #Creating our node,publisher and subscriber
        self.key_subscriber = rospy.Subscriber('/key_vel', Twist, self.callback)
        self.b_arm_publisher = rospy.Publisher('/elir/b_arm_trajectory_controller/command', JointTrajectory, queue_size=10)
        self.f_arm_publisher = rospy.Publisher('/elir/f_arm_trajectory_controller/command', JointTrajectory, queue_size=10)
        self.joints_subscriber = rospy.Subscriber('/elir/joint_states', JointState, self.callback_joints) 
        self.traction_f1_publisher = rospy.Publisher('elir/traction_f1_controller/command', Float64, queue_size=10)
        self.traction_f2_publisher = rospy.Publisher('elir/traction_f2_controller/command', Float64, queue_size=10)
        self.traction_b1_publisher = rospy.Publisher('elir/traction_b1_controller/command', Float64, queue_size=10)
        self.traction_b2_publisher = rospy.Publisher('elir/traction_b2_controller/command', Float64, queue_size=10)
        self.f_arm_joints = ['joint1_f', 'joint2_f']
        self.b_arm_joints = ['joint1_b', 'joint2_b']
        self.trajectory_duration = rospy.rostime.Duration(0.8)
        rospy.spin()

    #Callback function implementing the pose value received
    def callback_joints(self, msg):
        self.current_joint1b = msg.position[2]
        self.current_joint1f = msg.position[3] 	

    def callback(self, data):
        #Verifies if is a null value on angular z
        if data.angular.z == 0:
            pass
	#Verifies the joints position
        if(self.current_joint1b == 0 and self.current_joint1f == 0):       
            pass

        time = rospy.get_time()
        #Configure b_arm parameters
        msg_to_b_arm = JointTrajectory()                    
        msg_to_b_arm.joint_names = self.b_arm_joints        
        msg_to_b_arm.points = []                       
        points_to_b_arm = JointTrajectoryPoint()            
        points_to_b_arm.time_from_start = self.trajectory_duration

        #Configure f_arm parameters     
	msg_to_f_arm = JointTrajectory()                   
        msg_to_f_arm.joint_names = self.f_arm_joints        
        msg_to_f_arm.points = []                           
        points_to_f_arm = JointTrajectoryPoint()        
        points_to_f_arm.time_from_start = self.trajectory_duration  

	#Creating message to publish on joints
        key_vel = self.current_joint1b + 3 * data.angular.z       
        key_vel_to_wheels = 3 * data.angular.z
        points_to_f_arm.positions = [key_vel, -key_vel]
        points_to_b_arm.positions = [key_vel, -key_vel]
        msg_to_b_arm.points.append(points_to_b_arm)
        msg_to_f_arm.points.append(points_to_f_arm)

        #Verifies the limits of key_vel value
        if(key_vel >= 3000 or key_vel <= -3000):
            key_vel = self.current_joint1b
            self.b_arm_publisher.publish(msg_to_b_arm)
            self.f_arm_publisher.publish(msg_to_f_arm)
            self.traction_f1_publisher.publish(key_vel_to_wheels)
            self.traction_f2_publisher.publish(-key_vel_to_wheels)
            self.traction_b1_publisher.publish(-key_vel_to_wheels)
            self.traction_b2_publisher.publish(key_vel_to_wheels)
	#Write the values of arm joints        
	else:
            self.b_arm_publisher.publish(msg_to_b_arm)
            self.f_arm_publisher.publish(msg_to_f_arm)
            self.traction_f1_publisher.publish(key_vel_to_wheels)
            self.traction_f2_publisher.publish(-key_vel_to_wheels)
            self.traction_b1_publisher.publish(-key_vel_to_wheels)
            self.traction_b2_publisher.publish(key_vel_to_wheels)

if __name__ == '__main__':
    try:
        rospy.init_node('elir_line_controller', anonymous=True)
        x = arm_mimic_control()
    except rospy.ROSInterruptException: pass
