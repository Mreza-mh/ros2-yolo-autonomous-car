# SmartBot Refactoring Summary (Dec 22, 2025)

## ✅ تغییرات انجام شده

### 1. حذف شد

- ❌ `traffic_sign_decision.py` — نود اضافی

### 2. ساده‌سازی و تمیزکاری

#### **yolo_detector.py**

- ✂️ حذف `Float32MultiArray` و `vision_msgs` (اضافی)
- ✂️ حذف `max_det` parameter
- ✂️ حذف GPU/CPU selection (پیچیده‌کننده)
- ✂️ حذف تصویر visualization (یا استفاده از `yolo_visualizer`)
- ✂️ حذف frame counter
- ✨ **Output**: تنها `JSON` detections

#### **cmd_vel_mux.py**

- ✂️ حذف متغیرهای نام غیر ضروری
- ✅ اضافه: پارامتر `turn_duration_ms` (همگام‌سازی)
- ✅ **Format**: `LEFT:1500` / `RIGHT:1500` / `STOP`
- ✨ **نتیجه**: تک‌خطی و واضح

#### **esp32_bridge.py**

- ✂️ حذف کلمات طبیعی زبان
- ✂️ حذف `auto_forward_enabled` flag
- ✅ اضافه: parsing `CMD:duration`
- ✅ **نام تغییر**: `ESP32BridgeSmart` → `ESP32Bridge`
- ✨ **نتیجه**: Lightweight UDP bridge

#### **image_proc.py**

- ✂️ حذف توضیحات اضافی
- ✨ نگهداری: letterbox + CameraInfo

#### **android_camera.py**

- ✂️ ساده‌سازی reconnect logic
- ✂️ حذف frame counter

#### **ultrasonic_front.py**

- ✂️ ساده‌سازی نامگذاری و توضیحات
- ✨ نگهداری: 3 حالت (sim/serial/udp)

#### **obstacle_avoidance.py**

- ✂️ حذف توضیحات اضافی
- ✨ نگهداری: منطق اجتناب

#### **yolo_visualizer.py**

- ✂️ حذف متغیر `wait_key_delay`
- ✨ ساده: فقط نمایش

### 3. فایل‌های پیکربندی

#### **setup.py**

- ❌ حذف: `traffic_sign_decision`
- ❌ حذف: `yolo_drawer`
- ✨ 8 نود فعال

#### **smart_bot_launch.py**

- ✂️ ساده و سازمان‌یافته
- ✅ تمام 8 نود فعال
- ✨ گروه‌بندی منطقی

#### **params.yaml**

- ✂️ حذف پارامترهای غیر استفاده‌شده
- ✂️ حذف `traffic_sign_decision`
- ✂️ حذف پارامترهای اضافی
- ✨ تنها پارامترهای ضروری

---

## 📊 معماری نهایی

```
📷 Camera (android_camera)
    ↓
🖼️ Image Processing (image_proc: 640×640 + letterbox)
    ↓
🔍 YOLO Detector (yolo_detector: JSON)
    ↓
📋 /yolo/detections_json
    ├─→ 📊 Visualizer (yolo_visualizer)
    └─→ ⚡ CMD Mux (cmd_vel_mux: YOLO → CMD)
         ├─→ 📡 Ultrasonic (ultrasonic_front: Range)
         ├─→ 🛑 Obstacle Avoidance (obstacle_avoidance: Twist)
         └─→ 🔗 ESP32 Bridge (esp32_bridge: UDP)
             ↓
         🤖 ESP32
```

---

## 🔄 Flow دستورات

### سناریو 1: YOLO Detection

```
YOLO detects: "left_turn" (conf: 0.86)
↓
cmd_vel_mux: sends "LEFT:1500"
↓
esp32_bridge: parses duration → UDP
↓
ESP32: executes LEFT turn for 1.5s
```

### سناریو 2: Obstacle

```
Ultrasonic: 0.45m (< min_distance)
↓
obstacle_avoidance: sends Twist (backoff + turn)
↓
[Manual routing or prioritization in cmd_vel_mux]
```

---

## 📝 نقاط مهم

1. **YOLO Duration**: `turn_duration_ms` از `cmd_vel_mux` استفاده می‌شود
2. **ESP32 Parsing**: `LEFT:1500` format support اضافه شد
3. **Keep-Alive**: `esp32_bridge` هر 0.5s FORWARD می‌فرستد
4. **Visualization**: `yolo_visualizer` تصویر YOLO را نمایش می‌دهد
5. **Params**: تمام پارامترها در `params.yaml`

---

## 🚀 دستور تست

```bash
# Build
cd ~/smart_bot_ros2
colcon build --packages-select smart_bot_ros2

# Launch
source install/setup.bash
ros2 launch smart_bot_ros2 smart_bot_launch.py

# Monitor topics
ros2 topic list
ros2 topic echo /yolo/detections_json
ros2 topic echo /esp32_cmd
```

---

## ✨ مزایای تغییرات

✅ کد **تمیزتر** و **ساده‌تر**  
✅ **بدون اضافیات** — فقط ضروری‌ها  
✅ **بهتر سازمان‌یافته** — منطقی و واضح  
✅ **آسان‌تر برای نگهداری** — کم کد اضافی  
✅ **بیشتر قابل اعتماد** — منطق ساده = کمتر bug
