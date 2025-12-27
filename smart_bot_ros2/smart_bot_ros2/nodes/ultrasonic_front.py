#!/usr/bin/env python3
"""
Ultrasonic Front Sensor
-----------------------
سنسور اولتراسونیک جلو: سیم | UDP | شبیه‌سازی
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Range
import serial
import socket
import random
import threading
import time


class UltrasonicFront(Node):
    """سنسور اولتراسونیک: 3 حالت (sim/serial/udp)"""

    def __init__(self):
        super().__init__('ultrasonic_front')

        self.declare_parameter('mode', 'sim')
        self.declare_parameter('sim_distance', 2.0)
        self.declare_parameter('serial_port', '/dev/ttyUSB0')
        self.declare_parameter('baudrate', 115200)
        self.declare_parameter('udp_port', 8888)
        self.declare_parameter('frame_id', 'ultra_front')

        mode = self.get_parameter('mode').value
        self.frame_id = self.get_parameter('frame_id').value
        self.mode = mode

        # Publisher
        self.pub = self.create_publisher(Range, '/range/front', 10)

        # State
        self.ser = None
        self.sock = None
        self.running = True
        self.last_distance = None

        # Setup based on mode
        if mode == 'serial':
            self.setup_serial()
        elif mode == 'udp':
            self.setup_udp()
            self.udp_thread = threading.Thread(target=self.udp_listener, daemon=True)
            self.udp_thread.start()

        # Publish loop
        self.create_timer(0.08, self.publish_distance)
        self.get_logger().info(f'✓ Ultrasonic: {mode.upper()}')

    def setup_serial(self):
        """Setup serial connection"""
        try:
            port = self.get_parameter('serial_port').value
            baud = self.get_parameter('baudrate').value
            self.ser = serial.Serial(port, baud, timeout=0.1)
            self.get_logger().info(f'Serial: {port} @ {baud}')
        except Exception as e:
            self.get_logger().error(f'Serial error: {e}')

    def setup_udp(self):
        """Setup UDP socket"""
        try:
            port = self.get_parameter('udp_port').value
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(('0.0.0.0', port))
            self.sock.setblocking(False)
            self.get_logger().info(f'UDP port: {port}')
        except Exception as e:
            self.get_logger().error(f'UDP error: {e}')

    def udp_listener(self):
        """UDP receive thread"""
        while self.running and self.sock:
            try:
                data, _ = self.sock.recvfrom(64)
                s = data.decode('utf-8', errors='ignore').strip()

                # Parse: "123.45" or "D:123.45"
                if s.replace('.', '').replace('-', '').isdigit():
                    self.last_distance = float(s) / 100.0
                elif ':' in s:
                    try:
                        val = s.split(':')[1].strip()
                        if val.replace('.', '').replace('-', '').isdigit():
                            self.last_distance = float(val) / 100.0
                    except:
                        pass
            except BlockingIOError:
                time.sleep(0.001)
            except Exception as e:
                if self.running:
                    self.get_logger().warn(f'UDP error: {e}')
                time.sleep(0.1)

    def read_serial(self) -> float:
        """Read from serial"""
        if not self.ser or not self.ser.is_open:
            return None

        try:
            if self.ser.in_waiting > 0:
                line = self.ser.readline().decode('utf-8', errors='ignore').strip()

                if line.replace('.', '').replace('-', '').isdigit():
                    return float(line) / 100.0

                elif ':' in line:
                    try:
                        val = line.split(':')[1].strip()
                        if val.replace('.', '').replace('-', '').isdigit():
                            return float(val) / 100.0
                    except:
                        pass
        except serial.SerialException:
            self.ser.close()
        except Exception as e:
            self.get_logger().error(f'Serial read error: {e}')

        return None

    def publish_distance(self):
        """Publish Range message"""
        distance = None

        if self.mode == 'sim':
            base = self.get_parameter('sim_distance').value
            distance = base + random.uniform(-0.03, 0.03)
        elif self.mode == 'serial':
            if not self.ser or not self.ser.is_open:
                self.setup_serial()
            else:
                distance = self.read_serial()
        elif self.mode == 'udp':
            if self.last_distance is not None:
                distance = self.last_distance

        if distance is not None:
            distance = max(0.02, min(4.0, distance))

            msg = Range()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = self.frame_id
            msg.radiation_type = Range.ULTRASOUND
            msg.field_of_view = 0.52
            msg.min_range = 0.02
            msg.max_range = 4.0
            msg.range = float(distance)

            self.pub.publish(msg)

    def destroy_node(self):
        self.running = False

        if self.mode == 'udp' and hasattr(self, 'udp_thread'):
            if self.sock:
                try:
                    self.sock.close()
                except:
                    pass

        if self.ser and self.ser.is_open:
            self.ser.close()

        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = UltrasonicFront()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
