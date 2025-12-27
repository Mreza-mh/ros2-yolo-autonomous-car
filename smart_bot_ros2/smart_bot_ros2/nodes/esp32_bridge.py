#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import socket


class ESP32Bridge(Node):
    def __init__(self):
        super().__init__('esp32_bridge')

        # Read parameters from params.yaml
        self.declare_parameter('udp_ip', '10.89.52.115')
        self.declare_parameter('esp32_port', 8889)
        
        self.udp_ip = self.get_parameter('udp_ip').value
        self.udp_port = self.get_parameter('esp32_port').value

        # Create UDP socket (UDP is connectionless, no connect() needed)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Subscribe to ESP32 commands
        self.sub = self.create_subscription(
            String,
            '/esp32_cmd',
            self.cmd_callback,
            10
        )

        self.get_logger().info('ESP32 Bridge STARTED')
        self.get_logger().info(f'UDP target: {self.udp_ip}:{self.udp_port}')
        self.get_logger().info('Waiting for commands on topic: /esp32_cmd')

    def cmd_callback(self, msg: String):
        """Callback when ESP32 command is received from ROS topic"""
        if not msg.data:
            return
            
        cmd = msg.data.strip().upper()
        self.get_logger().info(f'ROS RECEIVED: [{cmd}]')
        try:
            print(f'ROS RECEIVED: {cmd}', flush=True)
        except Exception:
            pass

        # Validate command
        valid_commands = ['LEFT', 'RIGHT', 'GO', 'STOP']
        if cmd not in valid_commands:
            self.get_logger().warn(f'IGNORED CMD: [{cmd}] (valid: {valid_commands})')
            return

        # Send via UDP - use ASCII encoding (UTF-8 for ASCII is the same)
        try:
            # Ensure command ends with null terminator for ESP32 String handling
            cmd_bytes = cmd.encode('ascii')
            bytes_sent = self.sock.sendto(cmd_bytes, (self.udp_ip, self.udp_port))
            self.get_logger().info(f'UDP SENT: [{cmd}] ({bytes_sent} bytes) -> {self.udp_ip}:{self.udp_port}')
            try:
                print(f'UDP SENT: {cmd} -> {self.udp_ip}:{self.udp_port} ({bytes_sent} bytes)', flush=True)
            except Exception:
                pass
        except socket.error as e:
            self.get_logger().error(f'UDP SOCKET ERROR: {e}')
        except Exception as e:
            self.get_logger().error(f'UDP ERROR: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = ESP32Bridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down ESP32 Bridge...')
    finally:
        # Send STOP command before shutdown
        try:
            stop_cmd = 'STOP'.encode('utf-8')
            node.sock.sendto(stop_cmd, (node.udp_ip, node.udp_port))
            node.get_logger().info('Sent STOP command to ESP32')
        except Exception:
            pass
        node.sock.close()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
