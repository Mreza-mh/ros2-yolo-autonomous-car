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

## لینک دادن داخل README
- عکس:
  - `![car](assets/images/car.jpg)`
- ویدیو (GitHub معمولاً embed نمی‌کند، اما لینک مستقیم کافی است):
  - `[Car run video](assets/videos/car_run.mp4)`

## نکته
اگر ویدیوها حجیم شدند، بهتر است از Git LFS استفاده شود.
