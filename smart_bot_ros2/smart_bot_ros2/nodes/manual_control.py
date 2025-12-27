#!/usr/bin/env python3
"""
Manual Control Node
-------------------
Unified manual controller combining the simple keyboard input
and the curses-based control panel. Supports commands: GO, LEFT,
RIGHT, STOP. Run with `--ui` to use the curses UI, otherwise runs
in simple text-input mode.
"""

import sys
import threading
import curses

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class ManualControl(Node):
    """Unified manual control node.

    - `--ui` or `-u` : run curses UI (visual buttons)
    - otherwise runs a simple input loop (type key and Enter)
    """

    def __init__(self):
        super().__init__('manual_control')
        self.esp32_pub = self.create_publisher(String, '/esp32_cmd', 10)
        self.get_logger().info('Manual Control node started')

    def send_command(self, cmd: str):
        msg = String()
        msg.data = cmd
        self.esp32_pub.publish(msg)
        # Log via rclpy logger and also print to stdout so it's always visible
        self.get_logger().info(f'→ SENT: {cmd}')
        try:
            print(f'SENT: {cmd}', flush=True)
        except Exception:
            pass

    # --- simple text input mode ---
    def keyboard_input_loop(self):
        try:
            while rclpy.ok():
                try:
                    user_input = input('\n> ').strip().upper()
                except (EOFError, KeyboardInterrupt):
                    break

                if not user_input:
                    continue

                if user_input == 'Q':
                    self.get_logger().info('Quit requested')
                    break

                # Single-letter mappings
                if user_input == 'A':
                    self.send_command('LEFT')
                elif user_input == 'D':
                    self.send_command('RIGHT')
                elif user_input == 'W':
                    self.send_command('GO')
                elif user_input == 'S':
                    self.send_command('STOP')
                else:
                    # allow full commands
                    if user_input in ('LEFT', 'RIGHT', 'GO', 'STOP'):
                        self.send_command(user_input)
                    else:
                        self.get_logger().warn(f'Unknown command: {user_input}')
                        self.show_help()

        finally:
            rclpy.shutdown()

    # --- curses UI ---
    def run_ui(self, stdscr):
        curses.curs_set(0)
        stdscr.nodelay(1)
        stdscr.timeout(100)

        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        while rclpy.ok():
            stdscr.erase()
            h, w = stdscr.getmaxyx()

            title = '╔═ Manual Control (A:LEFT  G:GO  S:STOP  D:RIGHT  Q:QUIT) ═╗'
            stdscr.addstr(2, max(0, (w - len(title)) // 2), title, curses.color_pair(1))

            left_btn = '[ A - LEFT ]'
            go_btn = '[ G - GO ]'
            stop_btn = '[ S - STOP ]'
            right_btn = '[ D - RIGHT ]'

            row = h // 2
            x_left = w // 8
            x_go = x_left + len(left_btn) + 4
            x_stop = (w - len(stop_btn)) // 2
            x_right = w - w // 8 - len(right_btn)

            stdscr.addstr(row, x_left, left_btn, curses.color_pair(3))
            stdscr.addstr(row, x_go, go_btn, curses.color_pair(3))
            stdscr.addstr(row, x_stop, stop_btn, curses.color_pair(2))
            stdscr.addstr(row, x_right, right_btn, curses.color_pair(3))

            info_row = row + 3
            stdscr.addstr(info_row, 2, 'Press: A (LEFT) | G (GO) | S (STOP) | D (RIGHT) | Q (QUIT)')
            stdscr.addstr(info_row + 1, 2, 'ESP32 handles timing internally')

            stdscr.refresh()

            try:
                key = stdscr.getch()
                if key == ord('q') or key == ord('Q'):
                    break
                elif key == ord('a') or key == ord('A'):
                    self.send_command('LEFT')
                elif key == ord('g') or key == ord('G'):
                    self.send_command('GO')
                elif key == ord('d') or key == ord('D'):
                    self.send_command('RIGHT')
                elif key == ord('s') or key == ord('S'):
                    self.send_command('STOP')
            except Exception:
                # ignore drawing/input errors
                pass

    def show_help(self):
        self.get_logger().info('\nCommands:\nA, LEFT → LEFT\nD, RIGHT → RIGHT\nS, STOP → STOP\nW, GO → GO\nQ → QUIT\n')


def main(args=None):
    use_ui = False
    if args is None:
        args = sys.argv[1:]

    if '--ui' in args or '-u' in args:
        use_ui = True

    rclpy.init(args=None)
    node = ManualControl()

    try:
        # Start ROS spinning in a background thread so UI/input can run in foreground
        spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
        spin_thread.start()

        if use_ui:
            try:
                curses.wrapper(node.run_ui)
            except Exception as e:
                node.get_logger().error(f'curses UI failed: {e}. Falling back to text input.')
                node.keyboard_input_loop()
        else:
            node.get_logger().info('Running in text-input mode. Type commands and press Enter.')
            node.show_help()
            node.keyboard_input_loop()

    except KeyboardInterrupt:
        pass
    finally:
        try:
            stop_msg = String()
            stop_msg.data = 'STOP'
            node.esp32_pub.publish(stop_msg)
            node.get_logger().info('Sent STOP command on exit')
        except Exception:
            pass

        try:
            node.destroy_node()
        except Exception:
            pass

        rclpy.shutdown()


if __name__ == '__main__':
    main()
