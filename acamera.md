source /opt/ros/jazzy/setup.bash && cd /home/reza/smart_bot_ros2 && colcon build --symlink-install 2>&1 | tail -3
terminal قبلی هنوز فعال است. بذار kill کنم:


pkill -9 ros2

source /opt/ros/jazzy/setup.bash && cd /home/reza/smart_bot_ros2 && colcon build --symlink-install 2>&1 | tail -3
حالا دوباره launch کنیم:


source /opt/ros/jazzy/setup.bash && cd /home/reza/smart_bot_ros2 && source install/setup.bash && ros2 launch smart_bot_ros2 smart_bot_launch.py 2>&1 | grep -v "L+000A+000" | tail -80
Checked background terminal output

لازم است کمی صبر کنیم. بذار direct output ببینم:


source /opt/ros/jazzy/setup.bash && cd /home/reza/smart_bot_ros2 && source install/setup.bash && timeout 20 ros2 launch smart_bot_ros2 smart_bot_launch.py 2>&1 | head -100

🚀 شروع آماده‌سازی dataset...
   مسیر: ./smart_bot_ros2/dataset
   کلاس‌ها: right_turn, left_turn, stop

⚠️  هیچ تصویری پیدا نشد در: smart_bot_ros2/dataset/images
   لطفاً تصاویر را در این دایرکتوری قرار دهید.
   فرمت‌های پشتیبانی شده: .jpg, .jpeg, .png

   بعد از اضافه کردن تصاویر، دوباره این اسکریپت را اجرا کنید.

⚠️  لطفاً تصاویر و labels را اضافه کنید و دوباره اجرا کنید








sudo docker run -it --rm -v /dev:/dev --privileged --net=host microros/micro-ros-agent:jazzy udp4 --port 8889








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