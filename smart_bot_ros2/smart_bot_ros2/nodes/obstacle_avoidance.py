#!/usr/bin/env python3
"""
Obstacle Avoidance
------------------
اجتناب از موانع بر اساس سنسور اولتراسونیک
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Range
from geometry_msgs.msg import Twist


class ObstacleAvoidance(Node):
    """اجتناب از موانع: Range → Twist"""

    def __init__(self):
        super().__init__('obstacle_avoidance')

        self.declare_parameter('min_distance', 0.60)
        self.declare_parameter('critical_distance', 0.35)
        self.declare_parameter('backoff_speed', -0.22)
        self.declare_parameter('turn_speed', 0.9)
        self.declare_parameter('avoid_duration', 1.5)
        self.declare_parameter('cmd_timeout', 0.5)

        self.min_dist = self.get_parameter('min_distance').value
        self.critical_dist = self.get_parameter('critical_distance').value
        self.backoff = self.get_parameter('backoff_speed').value
        self.turn = self.get_parameter('turn_speed').value
        self.avoid_duration = self.get_parameter('avoid_duration').value

        # State
        self.last_obstacle_time = None
        self.obstacle_detected = False
        self.turn_direction = 1.0

        # Subscribers/Publishers
        self.create_subscription(Range, '/range/front', self.range_callback, 10)
        self.pub = self.create_publisher(Twist, '/cmd_vel_avoid', 10)

        self.create_timer(self.get_parameter('cmd_timeout').value, self.clear_cmd)
        self.get_logger().info('✓ Obstacle Avoidance started')

    def range_callback(self, msg: Range):
        """Process ultrasonic reading"""
        if msg.range > msg.max_range or msg.range < msg.min_range:
            return

        distance = msg.range
        now = self.get_clock().now()
        cmd = Twist()

        if distance < self.min_dist:
            # Obstacle detected
            if not self.obstacle_detected:
                self.turn_direction *= -1
                self.last_obstacle_time = now
                self.obstacle_detected = True

            # Critical zone
            if distance < self.critical_dist:
                cmd.linear.x = self.backoff * 1.3
                cmd.angular.z = 0.0
                self.get_logger().warn(f'CRITICAL: {distance:.2f}m')

            # Normal obstacle
            else:
                cmd.linear.x = self.backoff
                cmd.angular.z = self.turn * self.turn_direction
                self.get_logger().warn(f'OBSTACLE: {distance:.2f}m')

        else:
            # No obstacle
            if self.obstacle_detected:
                elapsed = (now - self.last_obstacle_time).nanoseconds / 1e9

                if elapsed < self.avoid_duration:
                    cmd.linear.x = self.backoff * 0.7
                    cmd.angular.z = self.turn * self.turn_direction * 0.6
                else:
                    self.obstacle_detected = False
                    cmd = Twist()

        self.pub.publish(cmd)

    def clear_cmd(self):
        """Reset command if not avoiding"""
        if not self.obstacle_detected:
            self.pub.publish(Twist())


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoidance()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.pub.publish(Twist())
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()


# ============================================================
# main — اجرای نود
# ============================================================
def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoidance()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.pub.publish(Twist())
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
