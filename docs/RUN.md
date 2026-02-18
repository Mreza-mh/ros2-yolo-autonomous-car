# Run SmartBot (build / launch / tools)

این فایل فقط همون دستورهاییه که خودم برای اجرا می‌زنم (برای اینکه سریع یادم بیاد).

> نکته: مسیر `~/smart_bot_ros2` اسم ورک‌اسپیس خودمه. اگر تو سیستم تو فرق داره، همون رو جایگزین کن.

## Build + Launch

```bash
cd ~/smart_bot_ros2
colcon build --packages-select smart_bot_ros2
source install/setup.bash
ros2 launch smart_bot_ros2 smart_bot_launch.py
```

## Build (Jazzy) + Manual UI

```bash
cd ~/smart_bot_ros2
source /opt/ros/jazzy/setup.bash
colcon build --packages-select smart_bot_ros2 --symlink-install
source install/setup.bash

# UI
ros2 run smart_bot_ros2 manual_control -- --ui
```

## micro-ROS agent (اختیاری)
اگر ESP32 رو با micro-ROS فلش کرده باشی (یا کلاً برای تست agent لازم داشته باشی)، اینو می‌تونی بالا بیاری:

```bash
sudo docker run -it --rm -v /dev:/dev --privileged --net=host microros/micro-ros-agent:jazzy udp4 --port 8889
```

## Tools

```bash
rviz2

rqt

# graph
rqt_graph
```

## نکته‌های سریع
- اگر یه دفعه همه‌چی قاطی شد و launchها باز موندن، من معمولاً اینو می‌زنم: `pkill -9 ros2`
- تنظیمات اصلی داخل `smart_bot_ros2/smart_bot_ros2/config/params.yaml` هست (IP ها، مسیر مدل، آدرس DroidCam، …)




cd ~/smart_bot_ros2
colcon build --packages-select smart_bot_ros2
source install/setup.bash
ros2 launch smart_bot_ros2 smart_bot_launch.py



ros2 run smart_bot_ros2 manual_control -- --ui

ros2 run smart_bot_ros2 manual_control


cd ~/smart_bot_ros2
source /opt/ros/jazzy/setup.bash
colcon build --packages-select smart_bot_ros2 --symlink-install
source install/setup.bash

# UI
ros2 run smart_bot_ros2 manual_control -- --ui

# or text mode
ros2 run smart_bot_ros2 manual_control
