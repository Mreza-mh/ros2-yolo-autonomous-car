#!/usr/bin/env python3
"""
YOLO Visualizer
---------------
نمایش تصاویر YOLO detections (با bounding boxes)
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import threading


class YOLOVisualizer(Node):
    """نمایش‌دهندهٔ تصاویر YOLO (با boxes)"""

    def __init__(self):
        super().__init__('yolo_visualizer')

        self.declare_parameter('image_topic', '/yolo/image_with_detections')
        self.declare_parameter('window_name', 'YOLO Detections')
        
        topic = self.get_parameter('image_topic').value
        window_name = self.get_parameter('window_name').value

        self.bridge = CvBridge()
        self.window_name = window_name
        self.last_image = None

        self.create_subscription(Image, topic, self.image_callback, 10)
        
        # Display thread
        self.display_thread = threading.Thread(target=self.display_loop, daemon=True)
        self.display_thread.start()
        
        self.get_logger().info(f'✓ Visualizer: {topic}')

    def image_callback(self, msg: Image):
        """دریافت تصویر و ذخیره برای نمایش"""
        try:
            self.last_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f'✗ Conversion error: {e}')

    def display_loop(self):
        """حلقهٔ نمایش تصاویر"""
        while rclpy.ok():
            if self.last_image is not None:
                try:
                    cv2.imshow(self.window_name, self.last_image)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                except Exception as e:
                    self.get_logger().error(f'✗ Display error: {e}')
            else:
                cv2.waitKey(10)


def main(args=None):
    rclpy.init(args=args)
    node = YOLOVisualizer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
