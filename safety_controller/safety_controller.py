#!/usr/bin/env python3
from ast import Tuple
from math import pi
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from ackermann_msgs.msg import AckermannDriveStamped, AckermannDrive
from visualization_msgs.msg import Marker
from rcl_interfaces.msg import SetParametersResult
from std_msgs.msg import Header
from safe_drive_msgs.msg import SafeDriveMsg


class SafetyController(Node):

    def __init__(self):
        super().__init__("safety_controller")

        self.declare_parameter("side", -1)

        self.safety_subscriber = self.create_subscription(SafeDriveMsg, "/safety_topic", self.drive_msg_callback, 10)
        self.safety_publisher = self.create_publisher(AckermannDriveStamped, "/drive", 10)
        self.SIDE = self.get_parameter('side').get_parameter_value().integer_value


    def drive_msg_callback(self, msg):
        """Processes the drive message."""

        scan = msg.scan
        drive_msg = msg.drive_msg.drive
        right_range = (31, 83)
        left_range = (17, 69)
        ranges = scan.ranges

        HARD_STOP_BOUND = 0.1
        SLOW_BOUND = 0.5

        if self.SIDE == -1:
            rng = range(*right_range, 2)
        else:
            rng = range(*left_range, 2)

        new_speed = drive_msg.speed
        for k in rng:
            average = 1/2 * (ranges[k] + ranges[k+1])
            if average < HARD_STOP_BOUND:
                new_speed = 0
                break
            if average < SLOW_BOUND:
                new_speed *= .5

        new_msg = AckermannDriveStamped()
        new_drive_msg = drive_msg
        new_drive_msg.speed = new_speed

        new_msg.drive = new_drive_msg
        new_msg.header = msg.drive_msg.header

        # Send drive
        self.safety_publisher.publish(new_msg)


def main():
    rclpy.init()
    safety_controller = SafetyController()
    rclpy.spin(safety_controller)
    safety_controller.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
