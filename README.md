# SmartBot ROS2 (YOLO + ESP32) 

![SmartBot Car](assets/images/car.jpg)

> این پروژه را به‌عنوان یک نمونه‌ی آموزشی/دانشگاهی برای پیاده‌سازی «خودروی خودران مبتنی بر ROS2» توسعه داده‌ام. در این سامانه، جریان تصویر از دوربین موبایل وارد ROS2 می‌شود، با YOLO پردازش می‌گردد و خروجی آن به فرمان‌های کنترلی ساده تبدیل شده و از طریق UDP برای ESP32 ارسال می‌شود تا در نهایت موتورهای خودرو کنترل شوند.

**فارسی** | [English](#english)

## فارسی

### در یک نگاه
- ورودی تصویر از موبایل (DroidCam) و پردازش در ROS2
- تشخیص علائم با **YOLOv8** و خروجی به‌صورت JSON
- ارسال فرمان‌ها با **UDP/IPv4** به ESP32 و کنترل موتور از طریق **TB6612FNG**
- ورودی YOLO در این پروژه روی **640×640** تنظیم شده تا توازن سرعت/دقت حفظ شود

### شرح عملکرد سامانه
جریان کلی به این صورت است:

1) تصویر از دوربین موبایل وارد ROS2 می‌شود (با DroidCam)  
2) تصویر برای YOLO پیش‌پردازش می‌شود (640×640 + letterbox)  
3) YOLO خروجی تشخیص‌ها را تولید می‌کند (به‌صورت JSON)  
4) فقط کلاس‌های `left_turn` / `right_turn` / `stop` به فرمان‌های `LEFT` / `RIGHT` / `STOP` تبدیل می‌شوند  
5) فرمان‌ها از طریق UDP به ESP32 ارسال می‌شوند و ESP32 منطق کنترل موتور را اجرا می‌کند

### مسیر فرمان تا موتور (Control Chain)
برای اینکه دقیق و قابل ارائه باشد، مسیر کنترل به‌صورت زیر است:

- **ROS2 → ESP32**: خروجی نود `cmd_vel_mux` روی تاپیک `/esp32_cmd` تولید می‌شود. نود `esp32_bridge` این پیام‌ها را به‌صورت **UDP/IPv4** و به شکل **رشته‌های ASCII** (مثل `LEFT`, `RIGHT`, `GO`, `STOP`) به IP/Port تعیین‌شده در `params.yaml` ارسال می‌کند.  
- **ESP32 → درایور موتور**: ESP32 فرمان را دریافت می‌کند و سیگنال‌های `IN1/IN2/PWM` را تولید می‌کند.  
- **درایور → موتور‌ها**: سیگنال‌ها وارد **ماژول TB6612FNG** می‌شوند و در نهایت به دو موتور خروجی می‌دهند (در این پروژه: یک موتور برای حرکت و یک موتور برای فرمان/چرخش).

### درباره خودِ ماشین (سخت‌افزار)
- شاسی خودرو با ترکیب قطعات **دو ماشین کنترلی اسباب‌بازی** ساخته شده و به‌عنوان پلتفرم مکانیکی پروژه استفاده شده است.
- برد کنترل: **ESP32-S3-CAM (ESP32-S3-N16R8) با دوربین OV5640**.  
  در این نسخه برای کیفیت بهتر تصویر و ساده‌تر شدن مسیر بینایی، از **دوربین موبایل نصب‌شده روی خودرو** و استریم DroidCam استفاده شده است (نه دوربین OV5640 روی برد).
- تغذیه: در وضعیت فعلی از **باتری کتابی ۹ ولت** به‌همراه **کاهنده‌ی ۹ به ۵ ولت** استفاده کرده‌ام.

### درایور موتور TB6612FNG (خلاصه‌ی Pinout)
ماژول درایور موتور دوکاناله TB6612FNG (یا TB6612FNG روی بردهای آماده) معمولاً این پایه‌ها را دارد:

- `VM`: ولتاژ موتور
- `VCC`: ولتاژ تغذیه بخش منطقی ماژول
- `GND`: زمین (معمولاً چند پایه‌ی GND دارد که به هم متصل‌اند)
- `A1`, `A2`: خروجی‌های موتور کانال A
- `B1`, `B2`: خروجی‌های موتور کانال B
- `PWMA`, `PWMB`: سیگنال کنترل سرعت برای موتورهای A و B (PWM)
- `AIN1`, `AIN2`: سیگنال‌های کنترلی جهت/حالت برای موتور A
- `BIN1`, `BIN2`: سیگنال‌های کنترلی جهت/حالت برای موتور B
- `STBY`: برای فعال بودن درایور باید این پایه `HIGH` باشد (خروج از حالت Standby)

> نکته: بسته به ترکیب سیگنال‌های کنترلی (`AIN1/AIN2` و `BIN1/BIN2`) حالت موتور (چرخش/ترمز/آزاد) تغییر می‌کند. در این پروژه، تولید این سیگنال‌ها داخل فریمور ESP32 انجام می‌شود.

### فناوری‌ها و ابزارهای استفاده‌شده
- ROS2 (نودها با `rclpy`)
- OpenCV + `cv_bridge` برای کار با تصویر
- `ultralytics` (YOLOv8)
- ESP32 (دریافت فرمان با UDP و کنترل موتور)
- دوربین: گوشی Android با DroidCam (استریم روی HTTP)

### پیش‌نیازها (خلاصه)
- Ubuntu + ROS2 (این پروژه عمدتاً با **Jazzy** توسعه و تست شده است)
- Python و پکیج‌های لازم (`opencv`, `ultralytics`, `pyserial`, …)
- گوشی Android + DroidCam (یا هر منبع تصویری که URL بده)
- ESP32 روی همان شبکه (یا در حالت Access Point) و پورت UDP فعال

### نودها (Nodes)
این‌ها نودهای اصلی داخل پکیج `smart_bot_ros2` هستند:

- `android_camera`: دریافت تصویر از DroidCam و انتشار روی `/camera/image_raw`
- `image_proc`: پیش‌پردازش تصویر برای YOLO و انتشار روی `/image_rect_color`
- `yolo_detector`: اجرای YOLOv8 و خروجی روی:
  - `/yolo/detections_json` (لیست تشخیص‌ها به صورت JSON)
  - `/yolo/image_with_detections` (تصویر با باکس‌ها)
- `cmd_vel_mux`: تبدیل تشخیص‌ها به فرمان‌های ساده و انتشار روی `/esp32_cmd`
- `esp32_bridge`: ارسال `/esp32_cmd` به ESP32 با UDP (پورت پیش‌فرض: `8889`)
- `manual_control`: کنترل دستی (حالت UI و حالت تایپی)
- `ultrasonic_front`: سنسور جلو (سه حالت: `sim` / `serial` / `udp`) و انتشار روی `/range/front`
- `obstacle_avoidance`: بر اساس `/range/front` یک خروجی `Twist` روی `/cmd_vel_avoid` منتشر می‌کند (برای توسعه‌های بعدی)
- `yolo_visualizer`: نمایش `/yolo/image_with_detections` با OpenCV

### معماری (نمای کلی)
به‌صورت خلاصه:

```
DroidCam -> /camera/image_raw
          -> image_proc -> /image_rect_color
          -> yolo_detector -> /yolo/detections_json -> cmd_vel_mux -> /esp32_cmd -> esp32_bridge -> UDP -> ESP32
                           -> /yolo/image_with_detections -> yolo_visualizer
```

تصویر زیر یک نمونه از گراف نودها/تاپیک‌ها (خروجی `rqt_graph`) پس از اجرای پروژه است:

![ROS2 Graph (rqt)](assets/images/rqt_graph.jpg)

### مدل YOLO (YOLOv8)
در این پروژه از YOLOv8 (کتابخانه‌ی `ultralytics`) استفاده شده است. مدل نهایی با داده‌های اختصاصی پروژه در Google Colab آموزش داده شده و خروجی آن در مسیر زیر قرار دارد:

- وزن‌ها (Weights): `smart_bot_ros2/smart_bot_ros2/runs/train/best/best.pt`
- کلاس‌های مورد استفاده در تصمیم‌گیری: `left_turn` / `right_turn` / `stop`

برای اجرای real-time، تصویر ورودی به مدل در ابعاد **640×640** و با روش **letterbox** آماده می‌شود (حفظ نسبت تصویر و جلوگیری از کشیدگی). در تست‌های عملی این پروژه، مدل برای سناریوهای تعریف‌شده‌ی پروژه دقت و پایداری مناسبی داشته و در حین حرکت خودرو نیز قابل استفاده بوده است.

نمونه‌ی خروجی YOLO (تصویر با bounding box) در تصویر زیر آمده است:

![YOLO Output](assets/images/yolo_output.jpg)

### ویدیوی دمو (عملکرد خودرو)
این ویدیو برای نمایش عملکرد خودرو در اجرای واقعی پروژه است:

[![مشاهده ویدیو](assets/images/car.jpg)](assets/videos/car_run.mp4)

> نکته: GitHub معمولاً فایل‌های `mp4` را داخل خودِ README به‌صورت پلیر نمایش نمی‌دهد؛ اما با کلیک روی تصویر، ویدیو باز می‌شود.

### مسیرهای مهم در پروژه
- تنظیمات: `smart_bot_ros2/smart_bot_ros2/config/params.yaml`
- لانچ اصلی: `smart_bot_ros2/smart_bot_ros2/launch/smart_bot_launch.py`
- فریمور ESP32: `smart_bot_ros2/smart_bot_ros2/firmware/ESP32_FIRMWARE_FINAL.ino`
- وزن مدل YOLO: `smart_bot_ros2/smart_bot_ros2/runs/train/best/best.pt`

### اجرا (Run)
برای دستورهای build و اجرا، به این فایل مراجعه کنید:
- `docs/RUN.md`

### پیش از اجرا (چک‌لیست)
پیش از اجرا، موارد زیر را بررسی می‌کنم تا از خطاهای رایج جلوگیری شود:

- در `params.yaml` آدرس DroidCam درست تنظیم شده است؟ (`camera_url`)
- مسیر مدل YOLO صحیح و قابل دسترس است؟ (`yolo_detector.model`)
- IP/Port مربوط به ESP32 درست است؟ (`esp32_bridge.udp_ip` و `esp32_bridge.esp32_port`)
- ESP32 به Wi‑Fi متصل است و روی پورت `8889` در حال دریافت UDP است؟

- پنجره‌ی `yolo_visualizer` (تصویر با باکس‌ها)
- `ros2 topic echo /yolo/detections_json` (خروجی JSON)

### تنظیمات مهم (Params)
پارامترهای اصلی از `params.yaml` خوانده می‌شوند. مواردی که معمولاً نیاز به تنظیم دارند:

- `android_camera.ros__parameters.camera_url` : آدرس DroidCam (IP گوشی + پورت)
- `yolo_detector.ros__parameters.model` : مسیر فایل مدل (`best.pt`)
- `esp32_bridge.ros__parameters.udp_ip` و `esp32_port` : IP و پورت ESP32
- `ultrasonic_front.ros__parameters.mode` : `sim` یا `serial` یا `udp`

### تاپیک‌های کلیدی
- تصویر خام: `/camera/image_raw`
- تصویر آماده برای YOLO: `/image_rect_color`
- خروجی YOLO (JSON): `/yolo/detections_json`
- تصویر با باکس‌ها: `/yolo/image_with_detections`
- فرمان خروجی برای ESP32: `/esp32_cmd`
- فاصله سنسور جلو: `/range/front`

### نکته درباره حرکت رو به جلو
در نسخه‌ی فعلی، تصمیم‌گیری بر اساس YOLO صرفاً روی **چپ/راست/ایست** متمرکز است. برای شروع حرکت رو به جلو، معمولاً ابتدا یک‌بار با `manual_control` فرمان `GO` ارسال می‌شود و سپس فرمان‌های `LEFT/RIGHT/STOP` توسط YOLO تولید و ارسال می‌گردند.

### نکات تکمیلی
- در `smart_bot_launch.py` برای YOLO یک venv با مسیر ثابت در نظر گرفته شده است (`/home/reza/smart_bot_ros2/yolo_env`). اگر مسیر شما متفاوت است، یا همان مسیر را ایجاد کنید، یا مسیر venv/نصب YOLO را با سیستم خود هماهنگ کنید.
- در نسخه‌ی فعلی، `obstacle_avoidance` صرفاً خروجی `/cmd_vel_avoid` تولید می‌کند. برای اثرگذاری روی حرکت خودرو، لازم است یک مرحله‌ی «تبدیل/ادغام» اضافه شود تا `Twist` به فرمان‌های ESP32 تبدیل گردد (در این نسخه متصل نشده است).

---

## English

### At a glance
- Mobile camera input (DroidCam) and processing in ROS2
- Sign detection with **YOLOv8** and JSON output
- Command delivery over **UDP/IPv4** to the ESP32 and motor control via **TB6612FNG**
- YOLO input is set to **640×640** to maintain a speed/accuracy trade-off

### System operation
The overall flow is:

1) Video from the mobile camera enters ROS2 (via DroidCam)  
2) The image is preprocessed for YOLO (640×640 + letterbox)  
3) YOLO produces detections (as JSON)  
4) Only the classes `left_turn` / `right_turn` / `stop` are mapped to the commands `LEFT` / `RIGHT` / `STOP`  
5) Commands are sent to the ESP32 via UDP, and the ESP32 executes the motor-control logic

### Control chain (Control Chain)
To keep it precise and presentable, the control chain is:

- **ROS2 → ESP32**: The `cmd_vel_mux` node publishes on `/esp32_cmd`. The `esp32_bridge` node sends these messages over **UDP/IPv4** as **ASCII strings** (e.g., `LEFT`, `RIGHT`, `GO`, `STOP`) to the IP/Port defined in `params.yaml`.  
- **ESP32 → motor driver**: The ESP32 receives the command and generates `IN1/IN2/PWM` signals.  
- **Driver → motors**: Signals go into the **TB6612FNG** module and drive two motors (in this project: one drive motor and one steering motor).

### About the car (hardware)
- The chassis is built by combining parts from **two toy RC cars**, used as the mechanical platform for the project.
- Controller board: **ESP32-S3-CAM (ESP32-S3-N16R8) with OV5640 camera**.  
  In this version, for higher image quality and a simpler vision pipeline, I use an **Android phone camera mounted on the car** via DroidCam stream (not the OV5640 on the board).
- Power: the current setup uses a **9V battery** + a **9V→5V buck converter**.

### TB6612FNG motor driver (pinout summary)
The TB6612FNG dual-channel motor driver module (or TB6612FNG on ready-made boards) typically provides these pins:

- `VM`: motor supply voltage
- `VCC`: logic supply voltage
- `GND`: ground (often multiple GND pins tied together)
- `A1`, `A2`: motor A outputs
- `B1`, `B2`: motor B outputs
- `PWMA`, `PWMB`: speed control signals for motors A and B (PWM)
- `AIN1`, `AIN2`: direction/mode control signals for motor A
- `BIN1`, `BIN2`: direction/mode control signals for motor B
- `STBY`: must be `HIGH` to enable the driver (exit standby)

> Note: depending on the combination of control signals (`AIN1/AIN2` and `BIN1/BIN2`), the motor mode (drive/brake/coast) changes. In this project, these signals are generated by the ESP32 firmware.

### Technologies and tools used
- ROS2 (nodes written in `rclpy`)
- OpenCV + `cv_bridge` for image handling
- `ultralytics` (YOLOv8)
- ESP32 (UDP command receiver + motor control)
- Camera: Android phone via DroidCam (HTTP stream)

### Prerequisites (summary)
- Ubuntu + ROS2 (this project was mainly developed and tested on **Jazzy**)
- Python and required packages (`opencv`, `ultralytics`, `pyserial`, …)
- Android phone + DroidCam (or any image source that provides a URL)
- ESP32 on the same network (or in Access Point mode) with UDP enabled

### Nodes (Nodes)
These are the main nodes in the `smart_bot_ros2` package:

- `android_camera`: receive frames from DroidCam and publish to `/camera/image_raw`
- `image_proc`: preprocess frames for YOLO and publish to `/image_rect_color`
- `yolo_detector`: run YOLOv8 and publish:
  - `/yolo/detections_json` (detections list as JSON)
  - `/yolo/image_with_detections` (image with bounding boxes)
- `cmd_vel_mux`: convert detections into simple commands and publish to `/esp32_cmd`
- `esp32_bridge`: send `/esp32_cmd` to the ESP32 over UDP (default port: `8889`)
- `manual_control`: manual control (UI mode and text-input mode)
- `ultrasonic_front`: front sensor (three modes: `sim` / `serial` / `udp`) and publish to `/range/front`
- `obstacle_avoidance`: based on `/range/front`, publish a `Twist` on `/cmd_vel_avoid` (for future development)
- `yolo_visualizer`: display `/yolo/image_with_detections` using OpenCV

### Architecture (high-level)
In short:

```
DroidCam -> /camera/image_raw
          -> image_proc -> /image_rect_color
          -> yolo_detector -> /yolo/detections_json -> cmd_vel_mux -> /esp32_cmd -> esp32_bridge -> UDP -> ESP32
                           -> /yolo/image_with_detections -> yolo_visualizer
```

The image below shows an example of the nodes/topics graph (output of `rqt_graph`) after running the project:

![ROS2 Graph (rqt)](assets/images/rqt_graph.jpg)

### YOLO model (YOLOv8)
This project uses YOLOv8 (the `ultralytics` library). The final model was trained in Google Colab using the project's custom dataset, and the output weights are stored here:

- Weights: `smart_bot_ros2/smart_bot_ros2/runs/train/best/best.pt`
- Classes used for decision-making: `left_turn` / `right_turn` / `stop`

For real-time execution, the input to the model is prepared at **640×640** using **letterbox** (keeps aspect ratio and avoids stretching). In practical tests for this project, the model has shown good accuracy and stability for the defined scenarios, and it remains usable while the car is moving.

An example YOLO output (image with bounding boxes) is shown below:

![YOLO Output](assets/images/yolo_output.jpg)

### Demo video (car in action)
This video demonstrates the car running in a real setup:

[![Watch video](assets/images/car.jpg)](assets/videos/car_run.mp4)

> Note: GitHub usually does not render `mp4` files as an inline player inside the README; clicking the image opens the video file.

### Key project paths
- Params: `smart_bot_ros2/smart_bot_ros2/config/params.yaml`
- Main launch: `smart_bot_ros2/smart_bot_ros2/launch/smart_bot_launch.py`
- ESP32 firmware: `smart_bot_ros2/smart_bot_ros2/firmware/ESP32_FIRMWARE_FINAL.ino`
- YOLO weights: `smart_bot_ros2/smart_bot_ros2/runs/train/best/best.pt`

### Run
For build and run commands, see:
- `docs/RUN.md`

### Pre-run checklist
Before running, I check the following to avoid common issues:

- Is the DroidCam URL set correctly in `params.yaml`? (`camera_url`)
- Is the YOLO model path correct and accessible? (`yolo_detector.model`)
- Are the ESP32 IP/port correct? (`esp32_bridge.udp_ip` and `esp32_bridge.esp32_port`)
- Is the ESP32 connected to Wi‑Fi and receiving UDP on port `8889`?

- `yolo_visualizer` window (image with bounding boxes)
- `ros2 topic echo /yolo/detections_json` (JSON output)

### Important parameters (Params)
The main parameters are read from `params.yaml`. The ones typically adjusted are:

- `android_camera.ros__parameters.camera_url` : DroidCam URL (phone IP + port)
- `yolo_detector.ros__parameters.model` : model path (`best.pt`)
- `esp32_bridge.ros__parameters.udp_ip` and `esp32_port` : ESP32 IP and port
- `ultrasonic_front.ros__parameters.mode` : `sim` or `serial` or `udp`

### Key topics
- Raw image: `/camera/image_raw`
- YOLO input image: `/image_rect_color`
- YOLO output (JSON): `/yolo/detections_json`
- Image with bounding boxes: `/yolo/image_with_detections`
- ESP32 command output: `/esp32_cmd`
- Front sensor range: `/range/front`

### Note on forward motion
In the current version, YOLO-based decision-making focuses only on **left/right/stop**. To start forward motion, I usually send a `GO` command once using `manual_control`, then YOLO continues with `LEFT/RIGHT/STOP`.

### Additional notes
- In `smart_bot_launch.py`, a YOLO venv with a fixed path is assumed (`/home/reza/smart_bot_ros2/yolo_env`). If your path differs, either create that path or adjust to match your local venv/installation.
- In the current version, `obstacle_avoidance` only produces `/cmd_vel_avoid`. For it to affect the car motion, an extra “conversion/merge” stage is needed to convert `Twist` into ESP32 commands (not wired in this version).
