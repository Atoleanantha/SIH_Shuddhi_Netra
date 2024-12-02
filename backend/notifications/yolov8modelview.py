import cloudinary
import cloudinary.uploader
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from ultralytics import YOLO
import numpy as np
from PIL import Image
import os
import cv2
from django.conf import settings
from datetime import datetime  # Import datetime to get the current timestamp

# Load the custom YOLOv8 model
model = YOLO('C:/Users/atole/Documents/Projects/SIH/SIH_Shuddhi/backend/notifications/best.pt')

# Class names for detection
CLASS_NAMES = {
    0: 'cardboard', 
    1: 'dustbin', 
    2: 'paper', 
    3: 'paper-bottle-teacups-wrapper', 
    4: 'plastic_bag', 
    5: 'plastic_bottle', 
    6: 'plastic_cap', 
    7: 'plastic_food_container', 
    8: 'plastic_wrapper', 
    9: 'spit', 
    10: 'tea_cup', 
    11: 'tea_cup_cap', 
    12: 'wooden_stick'
}

class CustomDetection():

    
    def detect_waste(self, file_obj):
        """Process image and detect waste using YOLO."""
        pil_image = Image.open(file_obj).convert('RGB')
        img = np.array(pil_image)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # Run YOLO model
        results = model.predict(img, imgsz=640)
        detections = []
        for result in results[0].boxes:
            box = result.xyxy.numpy()[0]
            cls = result.cls.numpy().item()
            class_name = CLASS_NAMES.get(int(cls), "Unknown")
            confidence = result.conf.numpy().item()

            # Append detection info
            detections.append({
                "xmin": int(box[0]),
                "ymin": int(box[1]),
                "xmax": int(box[2]),
                "ymax": int(box[3]),
                "class_name": class_name,
                "confidence": confidence
            })

            # Draw bounding box and label on the image
            x_min, y_min, x_max, y_max = map(int, box)
            cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
            cv2.putText(
                img,
                f"{class_name} {confidence:.2f}",
                (x_min, y_min - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

        return detections, img

    def upload_to_cloudinary(self, processed_image):
        """Upload the processed image to Cloudinary."""
        _, buffer = cv2.imencode('.jpg', processed_image)
        img_bytes = buffer.tobytes()

        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(
            img_bytes,
            folder="waste_images"
        )
        return upload_result.get("secure_url")

    def notify_staff(self, notification):
        """Notify cleaning staff or escalate."""
        print(f"Notification: {notification.message}")
        # Send email/SMS/push notification logic here


# class CustomDetectionViewSet(APIView):
#     parser_classes = [MultiPartParser, FormParser]
#     permission_classes=[]
#     def post(self, request, *args, **kwargs):
#         try:
#             # Get the uploaded file
#             file_obj = request.FILES['image']
#             file_name = default_storage.save(file_obj.name, file_obj)
#             file_path = os.path.join(settings.MEDIA_ROOT, file_name)

#             # Load the image using PIL and convert to RGB
#             pil_image = Image.open(file_path).convert('RGB')  # Ensure image is in RGB format
#             img = np.array(pil_image)

#             # Convert RGB to BGR (OpenCV uses BGR format)
#             img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

#             # Run inference on the image
#             results = model.predict(img, imgsz=640)  # Adjust `imgsz` if needed

#             # Parse YOLOv8 results
#             detections = []
#             for result in results[0].boxes:
#                 box = result.xyxy.numpy()[0]  # Get bounding box
#                 cls = result.cls.numpy().item()  # Class ID
#                 class_name = CLASS_NAMES.get(int(cls), "Unknown")
#                 score = result.conf.numpy().item()

#                 # Draw bounding boxes on the image
#                 x_min, y_min, x_max, y_max = map(int, box)
#                 cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
#                 cv2.putText(
#                     img,
#                     f"{class_name} {score:.2f}",
#                     (x_min, y_min - 10),
#                     cv2.FONT_HERSHEY_SIMPLEX,
#                     0.5,
#                     (0, 255, 0),
#                     2
#                 )

#                 # Append the detection result
#                 detections.append({
#                     "xmin": int(box[0]),
#                     "ymin": int(box[1]),
#                     "xmax": int(box[2]),
#                     "ymax": int(box[3]),
#                     "class_name": class_name,
#                     "confidence": score
#                 })

#             # Get the current timestamp and format it
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

#             # Create a unique file name using the timestamp
#             unique_filename = f"{timestamp}_{file_name}"

#             # Convert the image to a format that Cloudinary can upload (e.g., PNG or JPEG)
#             _, buffer = cv2.imencode('.jpg', img)
#             img_bytes = buffer.tobytes()

#             # Upload the image to Cloudinary
#             upload_result = cloudinary.uploader.upload(
#                 img_bytes,
#                 folder='detected_images',  # Specify a folder in Cloudinary
#                 public_id=unique_filename.split('.')[0]  # Use the unique filename (without extension)
#             )

#             # Get the URL of the uploaded image
#             cloudinary_image_url = upload_result.get('url')

#             # Clean up saved image
#             default_storage.delete(file_name)

#             # Return the Cloudinary URL along with detections
#             return Response({
#                 "image_url": cloudinary_image_url,
#                 "detections": detections
#             })

#         except Exception as e:
#             return Response({"error": str(e)}, status=500)
