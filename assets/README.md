# assets/

این پوشه برای نگهداری عکس‌ها و ویدیوهای پروژه است تا ریپو مرتب و قابل ارائه باشد.

## ساختار پیشنهادی

- `assets/images/` (عکس‌ها و اسکرین‌شات‌ها)
- `assets/videos/` (ویدیوها)

## فایل‌هایی که برای README اصلی در نظر گرفتم
اگر این نام‌ها رعایت شوند، `README.md` بدون تغییر به‌درستی نمایش داده می‌شود:

- عکس خودرو: `assets/images/car.jpg`
- گراف نودها (از `rqt`/`rqt_graph`): `assets/images/rqt_graph.jpg`
- نمونه خروجی YOLO (تصویر با bounding box): `assets/images/yolo_output.jpg`
- ویدیوی حرکت خودرو: `assets/videos/car_run.mp4`

## راهنمای تهیه اسکرین‌شات
- **نودها/گراف**: از `rqt_graph` اسکرین‌شات تهیه کنید (یا داخل `rqt` بخش Graph).
- **خروجی YOLO**: از یکی از موارد زیر اسکرین‌شات تهیه کنید:
  - پنجره‌ی `yolo_visualizer`
  - یا نمایش تاپیک `/yolo/image_with_detections` در ابزارهای تصویر داخل ROS2 (مثل `rqt`-based viewers)

## نکته درباره ویدیو در README
GitHub معمولاً فایل‌های `mp4` را داخل خودِ README به‌صورت پلیر نمایش نمی‌دهد. برای همین در `README.md` یک تصویر (thumbnail) گذاشته شده که با کلیک روی آن، فایل ویدیو باز می‌شود.

