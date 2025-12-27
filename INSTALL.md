# دستورالعمل نصب و راه‌اندازی SmartBot ROS2

## 📋 نیازمندی‌ها

- ROS2 Humble یا بالاتر
- Python 3.10+
- Ubuntu 22.04+ (یا دیگر توزیع‌های Linux)
- colcon (ROS2 build tool)

## 🛠️ مراحل نصب

### 1. نصب وابستگی‌های سیستمی

```bash
# Update packages
sudo apt update
sudo apt upgrade -y

# Install ROS2 build tools
sudo apt install -y python3-colcon-common-extensions
sudo apt install -y python3-rosdep

# Install dependencies
sudo apt install -y \
    python3-dev \
    python3-pip \
    libopencv-dev \
    python3-opencv

# Install serial tools
sudo apt install -y ros-humble-vision-msgs
```

### 2. نصب وابستگی‌های Python

```bash
pip install --upgrade pip
pip install \
    opencv-python \
    pyserial \
    ultralytics \
    numpy
```

### 3. ساخت پروژه

```bash
cd ~/smart_bot_ros2

# Install dependencies
rosdep install --from-paths src --ignore-src -r -y

# Build
colcon build

# Source
source install/setup.bash
```

## 🚀 راه‌اندازی

### گزینه 1: راه‌اندازی تمام نودها

```bash
ros2 launch smart_bot_ros2 smart_bot_launch.py
```

### گزینه 2: راه‌اندازی نودهای مختلف

```bash
# Terminal 1: دوربین
ros2 run smart_bot_ros2 android_camera

# Terminal 2: پردازش تصویر
ros2 run smart_bot_ros2 image_proc

# Terminal 3: تشخیص YOLO
ros2 run smart_bot_ros2 yolo_detector

# Terminal 4: سنسور اولتراسونیک
ros2 run smart_bot_ros2 ultrasonic_front

# Terminal 5: اجتناب از مانع
ros2 run smart_bot_ros2 obstacle_avoidance

# Terminal 6: تتبع اشیاء
ros2 run smart_bot_ros2 object_follower

# Terminal 7: مالتیپلکسر دستورات
ros2 run smart_bot_ros2 cmd_vel_mux

# Terminal 8: پل ESP32
ros2 run smart_bot_ros2 esp32_bridge

# Terminal 9: نظارت وضعیت
ros2 run smart_bot_ros2 state_monitor
```

## 📊 مشاهده تاپیک‌ها

```bash
# لیست تمام تاپیک‌ها
ros2 topic list

# مشاهده پیام‌های دوربین
ros2 topic echo /camera/image_raw

# مشاهده نتایج تشخیص YOLO
ros2 topic echo /yolo/detections

# مشاهده فاصله سنسور اولتراسونیک
ros2 topic echo /ultrasonic/front/range

# مشاهده دستورات حرکتی
ros2 topic echo /cmd_vel

# مشاهده اطلاعات diagnostics
ros2 topic echo /diagnostics
```

## ⚙️ تغییر تنظیمات

تمام تنظیمات در فایل `smart_bot_ros2/config/params.yaml` هستند.

### مثال: تغییر دوربین

```yaml
android_camera:
  camera_id: 0 # 0 برای /dev/video0
  frame_width: 640
  frame_height: 480
  fps: 30
```

### مثال: تغییر کلاس هدف برای تتبع

```yaml
object_follower:
  target_class: "person" # 'dog', 'car', etc.
```

### مثال: تغییر فاصله خطر مانع

```yaml
obstacle_avoidance:
  danger_distance: 0.3 # متر
```

## 🔌 اتصال سخت‌افزار

### سنسور اولتراسونیک

```
HC-SR04 ↔ ESP32/Arduino
VCC ──→ 5V
GND ──→ GND
TRIG ──→ GPIO17
ECHO ──→ GPIO16
```

### دوربین

```
USB Camera ↔ Linux PC
/dev/video0 برای دوربین 0
/dev/video1 برای دوربین 1
```

### ESP32

```
ESP32 ↔ Linux PC
TX ──→ RX (FTDI/CH340)
RX ──→ TX
GND ──→ GND
```

## 🐛 حل مشکلات

### خطا: "Cannot import vision_msgs"

```bash
sudo apt install ros-humble-vision-msgs
```

### خطا: "Permission denied /dev/ttyUSB0"

```bash
# اضافه کردن کاربر به گروه dialout
sudo usermod -a -G dialout $USER

# و یا:
sudo chmod 666 /dev/ttyUSB0
```

### خطا: "Cannot import ultralytics"

```bash
pip install --upgrade ultralytics
```

### دوربین کار نمی‌کند

```bash
# لیست دستگاه‌های ویدیویی
ls -l /dev/video*

# تست دوربین
v4l2-ctl -d /dev/video0 -i

# یا استفاده از ffplay
ffplay /dev/video0
```

### سنسور سریال کار نمی‌کند

```bash
# لیست دستگاه‌های سریال
ls -l /dev/ttyUSB*
ls -l /dev/ttyACM*

# تست seriell:
screen /dev/ttyUSB0 9600
```

## 📈 بهبود عملکرد

### اگر CPU بالا است:

- کاهش FPS دوربین
- کاهش resolution
- استفاده از YOLO نسخه کوچکتر (yolov8n → yolov8s)

### اگر latency زیاد است:

- افزایش publish rate
- کاهش timeout
- بهتر کردن ترتیب اولویت‌ها

## 📚 منابع

- [ROS2 Humble Docs](https://docs.ros.org/en/humble/)
- [YOLOv8 Docs](https://docs.ultralytics.com/)
- [OpenCV Python](https://docs.opencv.org/master/d6/d00/tutorial_py_root.html)
- [PySerial Docs](https://pyserial.readthedocs.io/)

## 🆘 پشتیبانی

برای سوالات و مشکلات:

- ایمیل: mohrezmehri14@gmail.com
- GitHub Issues (if available)

---

**آخرین بروزرسانی**: November 25, 2025
