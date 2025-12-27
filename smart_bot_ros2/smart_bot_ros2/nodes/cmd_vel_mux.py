#!/usr/bin/env python3
"""
YOLO → ESP32 Direct Bridge
---------------------------
YOLO detections را دریافت کن → فرمان ESP32 بفرست
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json


class CmdVelMux(Node):
    """Direct: YOLO JSON → ESP32 Command"""

    def __init__(self):
        super().__init__('cmd_vel_mux')

        self.declare_parameter('min_confidence', 0.5)
        self.min_confidence = self.get_parameter('min_confidence').value

        # Subscriber: YOLO detections
        self.create_subscription(String, '/yolo/detections_json', self.on_detections, 10)

        # Publisher: ESP32 commands
        self.esp32_pub = self.create_publisher(String, '/esp32_cmd', 10)

        self.get_logger().info(f'✓ CmdVelMux started | min_confidence: {self.min_confidence}')

    def on_detections(self, msg: String):
        """YOLO JSON → ESP32 CMD"""
        try:
            detections = json.loads(msg.data)

            if not detections:
                return

            # بهترین detection برای کلاس‌های هدف
            best_det = None
            best_conf = 0.0

            for det in detections:
                class_name = det.get('class_name', '').lower()
                confidence = det.get('confidence', 0.0)

                if class_name in ['right_turn', 'left_turn', 'stop']:
                    if confidence > best_conf and confidence >= self.min_confidence:
                        best_conf = confidence
                        best_det = det

            if best_det is None:
                return

            class_name = best_det['class_name'].lower()

            # تبدیل به دستور ESP32 (بدون timing - ESP32 خود تایم رو داره)
            if class_name == 'left_turn':
                cmd_str = "LEFT"
            elif class_name == 'right_turn':
                cmd_str = "RIGHT"
            elif class_name == 'stop':
                cmd_str = "STOP"
            else:
                return

            # ارسال به ESP32
            esp32_msg = String()
            esp32_msg.data = cmd_str
            self.esp32_pub.publish(esp32_msg)
            self.get_logger().info(f'→ ESP32: {cmd_str} (conf: {best_conf:.2f})')

        except json.JSONDecodeError:
            self.get_logger().warn('✗ JSON decode error')
        except Exception as e:
            self.get_logger().error(f'✗ Error: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = CmdVelMux()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        stop_msg = String()
        stop_msg.data = "STOP"
        node.esp32_pub.publish(stop_msg)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
