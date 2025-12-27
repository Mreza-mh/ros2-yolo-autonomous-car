"""
SmartBot Launch File
--------------------
راه‌اندازی تمام نودهای ربات (YOLO + ESP32 + Sensors)
"""

from launch import LaunchDescription
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    pkg_share = get_package_share_directory('smart_bot_ros2')
    config_file = os.path.join(pkg_share, 'config', 'params.yaml')

    # تنظیم محیط venv برای YOLO
    venv_path = "/home/reza/smart_bot_ros2/yolo_env"
    yolo_env = os.environ.copy()
    yolo_env["PATH"] = f"{venv_path}/bin:" + yolo_env.get("PATH", "")
    yolo_env["PYTHONPATH"] = (
        f"{venv_path}/lib/python3.12/site-packages:" +
        yolo_env.get("PYTHONPATH", "")
    )

    return LaunchDescription([

        # =====================
        # 📷 دوربین
        # =====================
        Node(
            package='smart_bot_ros2',
            executable='android_camera',
            name='android_camera',
            parameters=[config_file],
            output='screen'
        ),

        # =====================
        # 🖼️ پردازش تصویر
        # =====================
        Node(
            package='smart_bot_ros2',
            executable='image_proc',
            name='image_proc',
            parameters=[config_file],
            output='screen'
        ),

        # =====================
        # 🤖 YOLO (venv)
        # =====================
        Node(
            package='smart_bot_ros2',
            executable='yolo_detector',
            name='yolo_detector',
            parameters=[config_file],
            output='screen',
            env=yolo_env
        ),

        # =====================
        # 📡 سنسور اولتراسونیک
        # =====================
        Node(
            package='smart_bot_ros2',
            executable='ultrasonic_front',
            name='ultrasonic_front',
            parameters=[config_file],
            output='screen'
        ),

        # =====================
        # 🛑 اجتناب از موانع
        # =====================
        Node(
            package='smart_bot_ros2',
            executable='obstacle_avoidance',
            name='obstacle_avoidance',
            parameters=[config_file],
            output='screen'
        ),

        # =====================
        # ⚡ YOLO → ESP32
        # =====================
        Node(
            package='smart_bot_ros2',
            executable='cmd_vel_mux',
            name='cmd_vel_mux',
            parameters=[config_file],
            output='screen'
        ),

        # =====================
        # 🔗 ESP32 UDP Bridge
        # =====================
        Node(
            package='smart_bot_ros2',
            executable='esp32_bridge',
            name='esp32_bridge',
            parameters=[config_file],
            output='screen'
        ),

        # =====================
        # 📊 نمایش تصویر
        # =====================
        Node(
            package='smart_bot_ros2',
            executable='yolo_visualizer',
            name='yolo_visualizer',
            output='screen'
        ),
    ])
