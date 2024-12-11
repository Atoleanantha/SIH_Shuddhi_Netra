
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.utils.timezone import now
from django.db.models import Q

from .consumers import NotificationConsumer
from .models import Notification
from waste_management.models import CleaningStaff
from .serializers import NotificationSerializer
from rest_framework.permissions import IsAuthenticated
from users.models import DivisionalOffice, SubDivisionalOffice
from post_office.models import PostOffice
from django.core.files.storage import default_storage
from rest_framework.parsers import MultiPartParser, FormParser
import os
from django.conf import settings
import smtplib
import cloudinary
import cloudinary.uploader
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from ultralytics import YOLO
import numpy as np
from PIL import Image
import cv2
from django.conf import settings
from datetime import datetime  # Import datetime to get the current timestamp
import base64
from django.core.files.base import ContentFile
from rest_framework.response import Response
from rest_framework import status
from twilio.rest import Client
import os
from rest_framework.exceptions import PermissionDenied
from django.conf import settings

from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync



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

    def notify_staff(self, notification,cleaningStaff):
        """Notify cleaning staff or escalate."""
        # Email credentials (static)
        SENDER_EMAIL = "shuddhinetra@gmail.com"  # Replace with your sender email
        EMAIL_PASSWORD = "qlth etnw odpb atjm"  # Replace with your app password
        
        ACCOUNT_SID = "AC951a2882f0de6fa160204263a1f084da"
        AUTH_TOKEN = "4f4089ad57ccfa0f8dddff583889a123"
        TWILIO_PHONE_NUMBER = "+17755045196"  # Replace with your Twilio phone number




        # Send email/SMS/push notification logic here
        print("notification",cleaningStaff.email)
        to_number = "+91"+cleaningStaff.contactNo
        to_email = cleaningStaff.email
        message = notification.message
        subject = "Post Office cleaning Alert!"
        
        
        if not to_number or not message:
            return Response({"error": "Both 'to_number' and 'message' are required."}, status=status.HTTP_400_BAD_REQUEST)
         # Prepare the email content
        text = f"Subject: {subject}\n\n{message}\n\n Imgae Link :- {notification.image}"
        
        client = Client(ACCOUNT_SID, AUTH_TOKEN)

        try:
            # Send email using smtplib
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(SENDER_EMAIL, EMAIL_PASSWORD)
                server.sendmail(SENDER_EMAIL, to_email, text)

            msg = client.messages.create(
                body=text,
                from_=TWILIO_PHONE_NUMBER,
                to=to_number
            )
            print(f"SMS And Email sent successfully! Message SID: {msg.sid} . {to_email}")
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


       
class NotificationViewSet(viewsets.ModelViewSet):
    # parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    '''
        +endpoint notify/notifications/

        {
            "image": "data:image/png;base64,<BASE64_ENCODED_IMAGE>",
            "message": "Waste detected at the post office."
        }
        
        '''
    def create(self, request, *args, **kwargs):
        user = request.user
        try:
            if not user.is_sub_divisional:
                return Response({"error": "Unauthorized User or Divisional office cannot create."}, status=status.HTTP_403_FORBIDDEN)

            # Extract the image from the request
            image_data = request.data.get('image')

            if isinstance(image_data, str) and image_data.startswith('data:image'):
                # Decode base64 image
                format, imgstr = image_data.split(';base64,')  # format == 'data:image/png'
                ext = format.split('/')[-1]  # Extract extension
                image_file = ContentFile(base64.b64decode(imgstr), name=f"upload.{ext}")
            else:
                # Fallback to regular file upload
                image_file = request.FILES.get('image')

            if not image_file:
                return Response({"error": "No image provided or invalid format."}, status=status.HTTP_400_BAD_REQUEST)

            model = CustomDetection()

            # Get the current user's associated division pincode
            current_user_division = SubDivisionalOffice.objects.get(user=user).pincode
            post_office = PostOffice.objects.get(pincode=current_user_division)
            cleaningStaff = CleaningStaff.objects.get(pincode=post_office)
            print(cleaningStaff.email)
            print(cleaningStaff.contactNo)

            # Detect waste and process image
            detections, processed_image = model.detect_waste(image_file)
            if len(detections) > 1:  # Threshold for significant waste
                cloudinary_url = model.upload_to_cloudinary(processed_image)
                notification = Notification.objects.create(
                    image=cloudinary_url,
                    message=f"Significant waste detected at pincode {post_office.pincode}. Immediate action required!",
                    level="SUBDIVISIONAL",
                    pincode=post_office,
                )
                model.notify_staff(notification=notification,cleaningStaff=cleaningStaff)
                NotificationConsumer.send_notification("Send notification")
                # Serialize the notification
                serializer = self.get_serializer(notification)
                return Response({"data": serializer.data ,"detections": detections}, status=status.HTTP_201_CREATED)

            return Response("Not created, No waste detected!", status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

       
    # def escalate_unresolved(self):
    #     """Automatically escalate unresolved notifications to divisional office."""
    #     unresolved_notifications = Notification.objects.filter(
    #         Q(is_resolved=False, level='SUBDIVISIONAL', escalation_time__lte=now())
    #     )
    #     for notification in unresolved_notifications:
    #         notification.escalate_to_divisional()
    #         print(f"Notification {notification.id} escalated to divisional office.")

    def perform_update(self, serializer):
        """Update a notification and handle its resolution."""
        notification = serializer.save()
        if notification.is_resolved and notification.level == 'SUBDIVISIONAL':
            print(f"Notification {notification.id} resolved at subdivisional level.")
        elif not notification.is_resolved and notification.level == 'DIVISIONAL':
            print(f"Alert! Notification {notification.id} requires action at subdivisional level.")
    
    # @action(detail=False,methods=['GET'],permission_classes=[IsAuthenticated])
    def get_queryset(self):
        """Filter notifications based on the user's role and pincode."""
        try:
            user = self.request.user
            if hasattr(user, 'is_sub_divisional') and user.is_sub_divisional:
                # Fetch notifications for the subdivisional office based on user's pincode
                user_pincode = SubDivisionalOffice.objects.get(user=user).pincode
                post_office = PostOffice.objects.get(pincode=user_pincode)
                notifications=Notification.objects.filter(pincode=user_pincode,level="SUBDIVISIONAL")
                # notification_details = []
                # for notification in notifications:
                #     try: 
                #         notification_details.append({
                #             "notification": notification,
                #             "post_office_name": post_office.name,
                #             "post_office_address": post_office.address,
                #             "post_office_division": post_office.division_pincode,  # ForeignKey to another PostOffice
                #         })
                #     except PostOffice.DoesNotExist:
                #         # Handle cases where the PostOffice is missing
                #         pass
                return notifications
            
            elif hasattr(user, 'is_divisional') and user.is_divisional:
                # Fetch notifications for all post offices under the divisional office
                division_pincode = DivisionalOffice.objects.get(user=user).pincode
                post_offices = PostOffice.objects.filter(division_pincode=division_pincode)
                notifications=Notification.objects.filter(pincode__in=post_offices, level="DIVISIONAL")
               

                return notifications
            return Notification.objects.none()  # No notifications for unauthorized users
        except PostOffice.DoesNotExist:
            return Response({"error": "User is not associated with a divisional office."}, status=status.HTTP_403_FORBIDDEN)
        
    


    # @action(detail=False,methods=['PUT',"PATCH"],permission_classes=[IsAuthenticated])
    def update(self, request, *args, **kwargs):
        """Handle the update logic for notifications based on user roles."""
        user = request.user
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        if hasattr(user, 'is_sub_divisional') and user.is_sub_divisional:
            if instance.level != 'SUBDIVISIONAL':
                return Response(
                    {"error": "You cannot update this notification. It has already been escalated to divisional level."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if instance.action_performed:
                return Response(
                    {"error": "You cannot update this notification. It has already updated."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            if 'action_performed' in request.data:
                instance.action_performed = request.data['action_performed']
                instance.is_resolved = request.data.get('is_resolved', True)
                instance.read = True
                instance.updatedAt = now()
                instance.save()
                return Response({"message": "Action performed updated successfully."}, status=status.HTTP_200_OK)

            return Response(
                {"error": "Invalid data. Subdivisional users can only update 'action_performed' and 'is_resolved'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if hasattr(user, 'is_divisional') and user.is_divisional:
            if instance.level != 'DIVISIONAL':
                return Response(
                    {"error": "You cannot update this notification. It is still under subdivisional control."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            if instance.response:
                return Response(
                    {"error": "Response already added. You cannot update this notification again."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            if 'response' in request.data:
                instance.response = request.data['response']
                instance.updatedAt = now()
                instance.read = True
                instance.save()
                return Response({"message": "Response added successfully."}, status=status.HTTP_200_OK)

            return Response(
                {"error": "Invalid data. Divisional users can only update the 'response' field."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"error": "Unauthorized action."}, status=status.HTTP_403_FORBIDDEN)
    
    # @action(detail=False, methods=['patch'], permission_classes=[IsAuthenticated])
    # def partial_update(self, request, *args, **kwargs):
    #     """Partial update alias for PATCH."""
    #     return self.update(request, *args, **kwargs)
    def perform_destroy(self, instance):
        # Ensure that only sub-divisional officers can delete cleaning staff
        if not self.request.user.is_sub_divisional:
            raise PermissionDenied("Only sub-divisional officers can delete cleaning staff.")
        
        # Proceed with deletion if the user is a sub-divisional officer
        instance.delete()
        return Response({"message:":"Succesfully Deleted!"},status=status.HTTP_202_ACCEPTED)

