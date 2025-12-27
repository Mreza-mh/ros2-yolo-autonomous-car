#!/usr/bin/env python3
"""
YOLO Detector Node
------------------
دریافت تصویر → اجرای YOLOv8 → JSON + Visualized
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import json

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None


class YOLODetectorNode(Node):
    """ماژول تشخیص YOLO: Image → JSON + Visualized"""

    def __init__(self):
        super().__init__('yolo_detector')

        self.declare_parameter('model', 'yolov8n.pt')
        self.declare_parameter('conf_threshold', 0.35)
        self.declare_parameter('iou_threshold', 0.45)
        self.declare_parameter('input_topic', '/image_rect_color')

        model_name = self.get_parameter('model').value
        conf_threshold = self.get_parameter('conf_threshold').value
        iou_threshold = self.get_parameter('iou_threshold').value
        input_topic = self.get_parameter('input_topic').value

        # بارگذاری مدل
        self.model = None
        if YOLO is not None:
            try:
                self.model = YOLO(model_name)
                self.get_logger().info(f'✓ YOLO loaded: {model_name}')
            except Exception as e:
                self.get_logger().error(f'✗ Failed to load YOLO: {e}')
        else:
            self.get_logger().error('✗ ultralytics not installed')

        # Subscriber/Publisher
        self.create_subscription(Image, input_topic, self.detect_objects, 10)
        self.json_pub = self.create_publisher(String, '/yolo/detections_json', 10)
        self.viz_pub = self.create_publisher(Image, '/yolo/image_with_detections', 10)
        self.bridge = CvBridge()

    # =====================================================================
    #                           YOLO Detection
    # =====================================================================
    def detect_objects(self, msg):
        """دریافت تصویر و اجرای YOLO → JSON + Visualized"""

        if self.model is None:
            return

        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

            results = self.model(
                cv_image,
                conf=self.get_parameter('conf_threshold').value,
                iou=self.get_parameter('iou_threshold').value,
                verbose=False
            )

            # استخراج detections به JSON
            detections_list = []
            if results and len(results) > 0:
                for box in results[0].boxes:
                    x1, y1, x2, y2 = map(float, box.xyxy[0].tolist())
                    conf = float(box.conf)
                    cls = int(box.cls)
                    class_name = self.model.names.get(cls, str(cls))

                    detections_list.append({
                        'class_id': cls,
                        'class_name': class_name,
                        'confidence': conf,
                        'bbox': [x1, y1, x2, y2]
                    })

            # انتشار JSON
            json_msg = String()
            json_msg.data = json.dumps(detections_list, ensure_ascii=False)
            self.json_pub.publish(json_msg)

            # انتشار تصویر visualized با bounding boxes
            if results and len(results) > 0:
                annotated_image = results[0].plot()
                viz_msg = self.bridge.cv2_to_imgmsg(annotated_image, encoding='bgr8')
                viz_msg.header = msg.header
                self.viz_pub.publish(viz_msg)

        except Exception as e:
            self.get_logger().error(f'Error in detection: {e}')


# =====================================================================
#                           main()
# =====================================================================
def main(args=None):
    rclpy.init(args=args)
    node = YOLODetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
