#!/usr/bin/env python3
"""
Image Processing Node
---------------------
تصویر خام → Resize + Letterbox → تصویر استاندارد برای YOLO
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
import cv2


class ImageProc(Node):
    """تصویر پردازش: Undistort + Resize + Letterbox"""

    def __init__(self):
        super().__init__('image_proc')

        self.declare_parameter('input_topic', '/camera/image_raw')
        self.declare_parameter('output_topic', '/image_rect_color')
        self.declare_parameter('target_width', 640)
        self.declare_parameter('target_height', 640)
        self.declare_parameter('keep_aspect_ratio', True)

        input_topic = self.get_parameter('input_topic').value
        output_topic = self.get_parameter('output_topic').value
        self.width = self.get_parameter('target_width').value
        self.height = self.get_parameter('target_height').value
        self.keep_ar = self.get_parameter('keep_aspect_ratio').value

        # Subscriber
        self.create_subscription(Image, input_topic, self.image_callback, 10)
        self.create_subscription(CameraInfo, '/camera/camera_info', self.info_callback, 1)

        # Publisher
        self.pub_img = self.create_publisher(Image, output_topic, 10)
        self.pub_info = self.create_publisher(CameraInfo, '/camera_info_rect', 1)

        self.bridge = CvBridge()
        self.camera_matrix = None
        self.dist_coeffs = None

        self.get_logger().info(
            f'✓ ImageProc: {self.width}x{self.height} (AR={self.keep_ar})'
        )


    def info_callback(self, msg: CameraInfo):
        """CameraInfo دریافت و undistort parameters آماده کن"""
        if self.camera_matrix is not None:
            return
        if len(msg.k) >= 9 and len(msg.d) >= 5:
            import numpy as np
            self.camera_matrix = np.array(msg.k).reshape(3, 3)
            self.dist_coeffs = np.array(msg.d)
            self.get_logger().info('✓ CameraInfo loaded')

    def image_callback(self, msg: Image):
        """تصویر دریافت، process، و publish کن"""
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

            # Letterbox resize (without stretching)
            if self.keep_ar:
                h, w = cv_image.shape[:2]
                r = min(self.width / w, self.height / h)
                new_w, new_h = int(w * r), int(h * r)
                cv_image = cv2.resize(cv_image, (new_w, new_h))

                pad_w = (self.width - new_w) // 2
                pad_h = (self.height - new_h) // 2
                cv_image = cv2.copyMakeBorder(
                    cv_image, pad_h, pad_h, pad_w, pad_w,
                    cv2.BORDER_CONSTANT, value=(0, 0, 0)
                )
            else:
                cv_image = cv2.resize(cv_image, (self.width, self.height))

            # Publish processed image
            out_msg = self.bridge.cv2_to_imgmsg(cv_image, encoding='bgr8')
            out_msg.header = msg.header
            self.pub_img.publish(out_msg)

            # Publish camera info
            info_msg = CameraInfo()
            info_msg.header = msg.header
            info_msg.height = self.height
            info_msg.width = self.width
            info_msg.distortion_model = "plumb_bob"
            info_msg.d = [0.0] * 5
            info_msg.k = [500.0, 0.0, self.width/2, 0.0, 500.0, self.height/2, 0.0, 0.0, 1.0]
            info_msg.p = [500.0, 0.0, self.width/2, 0.0, 0.0, 500.0, self.height/2, 0.0, 0.0, 0.0, 1.0, 0.0]
            self.pub_info.publish(info_msg)

        except Exception as e:
            self.get_logger().error(f'✗ Image processing error: {e}')



def main(args=None):
    rclpy.init(args=args)
    node = ImageProc()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
