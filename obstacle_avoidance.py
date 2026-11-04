#!/usr/bin/env python3
"""
Smart Obstacle Avoidance Node for ROS 2
Version: Random Explorer (The Drunken Sailor)
"""

import rclpy
import random
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from typing import List


class SmartAvoidanceNode(Node):
    def __init__(self):
        super().__init__('smart_avoidance')

        self.subscription = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10)
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)

        # Timer to stabilize wandering behavior (prevents jittery movement)
        self.wander_timer = 0
        self.wander_angular = 0.0

        # Status string for terminal logging
        self.robot_status = "START"

        self.get_logger().info('✅ Mode: Random Explorer Activated. Ready!')

    def scan_callback(self, msg: LaserScan):
        # --- 1. SENSOR DATA PROCESSING ---

        # Front Sector: +/- 20 degrees (Total 40 degrees)
        front_ranges = msg.ranges[0:20] + msg.ranges[340:360]

        # Side Sectors: Angled slightly forward to detect obstacles early
        left_ranges = msg.ranges[20:80]
        right_ranges = msg.ranges[280:340]

        # Helper function to filter noise (inf/nan) and get min distance
        def get_min_dist(ranges: List[float]) -> float:
            # Filter valid range: 0.05m to 10.0m
            clean = [x for x in ranges if x > 0.05 and x < 10.0]
            return min(clean) if clean else 10.0

        f_dist = get_min_dist(front_ranges)
        l_dist = get_min_dist(left_ranges)
        r_dist = get_min_dist(right_ranges)

        # --- 2. MOVEMENT LOGIC (STATE MACHINE) ---
        cmd = Twist()

        # STATE 1: EMERGENCY (< 0.25m)
        # Too close to an obstacle. Must reverse.
        if f_dist < 0.25:
            self.robot_status = "EMERGENCY"
            cmd.linear.x = -0.15
            # Reverse with a random twist to reorient the robot
            cmd.angular.z = random.choice([-0.5, 0.5])

        # STATE 2: OBSTACLE AVOIDANCE (0.25m - 0.7m)
        # Approaching obstacle. Slow down and maneuver.
        elif f_dist < 0.7:
            self.robot_status = "AVOID"
            # Keep moving forward slowly to encourage entering gaps
            cmd.linear.x = 0.10

            # RANDOM EXPLORATION LOGIC (Coin Flip):
            # If both Left and Right are relatively open (> 0.5m), pick a random direction.
            # This breaks the "wall-following" loop and forces the robot into the center.
            if l_dist > 0.5 and r_dist > 0.5:
                # Change direction every 20 frames to keep movement smooth
                if self.wander_timer % 20 == 0:
                    self.wander_angular = random.choice([-0.8, 0.8])
                cmd.angular.z = self.wander_angular

            # If one side is clearly blocked, use standard avoidance logic
            elif l_dist > r_dist:
                cmd.angular.z = 0.8  # Left is clearer
            else:
                cmd.angular.z = -0.8  # Right is clearer

            self.wander_timer += 1

        # STATE 3: CRUISING (> 0.7m)
        # Path is clear. Move fast.
        else:
            self.robot_status = "CRUISE"
            cmd.linear.x = 0.35

            # Wander Mode:
            # Apply slight random drifts while moving straight to mimic natural exploration.
            # Change drift direction every 50 frames (approx. 5 seconds).
            if self.wander_timer % 50 == 0:
                self.wander_angular = random.uniform(-0.3, 0.3)

            cmd.angular.z = self.wander_angular
            self.wander_timer += 1

        # Publish velocity command
        self.publisher_.publish(cmd)

        # Log status to terminal
        self.get_logger().info(
            f"[{self.robot_status}] Front: {f_dist:.2f}m | Left: {l_dist:.2f}m | Right: {r_dist:.2f}m"
        )


def main(args=None):
    rclpy.init(args=args)
    node = SmartAvoidanceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.publisher_.publish(Twist())  # Stop on Ctrl+C
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
