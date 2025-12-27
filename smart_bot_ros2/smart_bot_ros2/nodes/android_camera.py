#!/usr/bin/env python3
"""
Android Camera (DroidCam)
------------------------
دریافت تصویر از دوربین Android (DroidCam) و انتشار در ROS2
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
import cv2
import time
import threading


class AndroidCameraNode(Node):
    """دوربین Android: دریافت فریم و انتشار"""

    def __init__(self):
        super().__init__('android_camera')

        self.declare_parameter('camera_url', '')
        self.declare_parameter('source_fps', 20.0)
        self.declare_parameter('frame_id', 'camera_link')
        self.declare_parameter('width', 640)
        self.declare_parameter('height', 640)
        self.declare_parameter('reconnect_interval', 5.0)

        camera_url = self.get_parameter('camera_url').value
        self.target_fps = self.get_parameter('source_fps').value
        self.frame_id = self.get_parameter('frame_id').value
        self.width = self.get_parameter('width').value
        self.height = self.get_parameter('height').value
        reconnect_interval = self.get_parameter('reconnect_interval').value

        if not camera_url:
            self.get_logger().error('✗ camera_url not set!')
            raise RuntimeError('camera_url required')

        self.camera_url = camera_url
        self.cap = None
        self.connected = False
        self.running = True
        self.last_reconnect = time.time() - reconnect_interval
        self.reconnect_interval = reconnect_interval

        # Publishers
        self.pub_img = self.create_publisher(Image, '/camera/image_raw', 10)
        self.pub_info = self.create_publisher(CameraInfo, '/camera/camera_info', 1)
        self.bridge = CvBridge()
        self.camera_info = self._create_camera_info()

        # Publish loop
        self.create_timer(1.0 / max(self.target_fps, 1.0), self.publish_frame)

        # Reconnect thread
        self.connect_thread = threading.Thread(target=self._connect_worker, daemon=True)
        self.connect_thread.start()

        self.get_logger().info(f'✓ Camera: {camera_url}')

    def _create_camera_info(self) -> CameraInfo:
        """Create CameraInfo"""
        info = CameraInfo()
        info.height = self.height
        info.width = self.width
        info.distortion_model = "plumb_bob"
        
        fx = fy = 600.0
        cx = self.width / 2.0
        cy = self.height / 2.0
        
        info.d = [0.0] * 5
        info.k = [fx, 0.0, cx, 0.0, fy, cy, 0.0, 0.0, 1.0]
        info.r = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
        info.p = [fx, 0.0, cx, 0.0, 0.0, fy, cy, 0.0, 0.0, 0.0, 1.0, 0.0]
        
        return info

    def _connect_worker(self):
        """Reconnect thread"""
        while self.running:
            if not self.connected:
                current = time.time()
                if current - self.last_reconnect > self.reconnect_interval:
                    self._try_connect()
                    self.last_reconnect = current
            time.sleep(1.0)

    def _try_connect(self):
        """Try connect to camera"""
        try:
            self.get_logger().info('🔄 Connecting...')
            cap = cv2.VideoCapture(self.camera_url, cv2.CAP_FFMPEG)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            cap.set(cv2.CAP_PROP_FPS, self.target_fps)

            # Test
            ret, frame = cap.read()
            if ret and frame is not None:
                self.cap = cap
                self.connected = True
                self.get_logger().info('✅ Connected!')
            else:
                cap.release()
                self.connected = False
        except Exception as e:
            self.get_logger().error(f'✗ Connection error: {e}')
            self.connected = False

    def publish_frame(self):
        """Read frame and publish"""
        if not self.connected or self.cap is None:
            return

        try:
            ret, frame = self.cap.read()
            if not ret or frame is None:
                self.get_logger().warn('✗ No frame - reconnecting...')
                self.connected = False
                if self.cap:
                    try:
                        self.cap.release()
                    except:
                        pass
                self.cap = None
                return

            # Resize
            frame = cv2.resize(frame, (self.width, self.height))
            ts = self.get_clock().now().to_msg()

            # Publish Image
            img_msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
            img_msg.header.stamp = ts
            img_msg.header.frame_id = self.frame_id
            self.pub_img.publish(img_msg)

            # Publish CameraInfo
            info_msg = CameraInfo()
            info_msg.header.stamp = ts
            info_msg.header.frame_id = self.frame_id
            info_msg.height = self.camera_info.height
            info_msg.width = self.camera_info.width
            info_msg.distortion_model = self.camera_info.distortion_model
            info_msg.d = self.camera_info.d
            info_msg.k = self.camera_info.k
            info_msg.r = self.camera_info.r
            info_msg.p = self.camera_info.p
            self.pub_info.publish(info_msg)

        except Exception as e:
            self.get_logger().error(f'✗ Error: {e}')
            self.connected = False
            if self.cap:
                try:
                    self.cap.release()
                except:
                    pass
            self.cap = None

    def destroy_node(self):
        self.running = False
        if self.cap:
            try:
                self.cap.release()
            except:
                pass
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = AndroidCameraNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
