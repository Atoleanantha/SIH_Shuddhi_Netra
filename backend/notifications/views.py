
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.utils.timezone import now
from django.db.models import Q
from .models import Notification
from waste_management.models import CleaningStaff
from .serializers import NotificationSerializer
from rest_framework.permissions import IsAuthenticated
from users.api.permissions import IsDivisionalOffice,IsSubDivisionalOffice
from users.models import DivisionalOffice, SubDivisionalOffice
from post_office.models import PostOffice
from rest_framework.decorators import action


class NotificationViewSet(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated]
    # queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    # @action(detail=False,methods=['POST'],permission_classes=[IsAuthenticated& IsSubDivisionalOffice])
    def create(self, request, *args, **kwargs):
        '''
        +endpoint notify/notifications/

        {
            "image": "data:image/png;base64,<BASE64_ENCODED_IMAGE>",
            "message": "Waste detected at the post office."
        }
        
        '''
        user = request.user
        try:
            if not user.is_sub_divisional :
                return Response({"error": "Unauthorized User or Divisional office cannot create."}, status=status.HTTP_403_FORBIDDEN)
        
            # Get the current user's associated division pincode from DivisionalOffice
            print(user.is_sub_divisional)
            current_user_division = SubDivisionalOffice.objects.get(user=user).pincode

            #get post office
            post_office=PostOffice.objects.get(pincode=current_user_division).pincode

            # Add the division_pincode to the request data
            request.data['pincode'] = post_office

            # Serialize the data
            """Generate a new notification."""
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            if serializer.is_valid():  # Check if the data is valid
                notification = serializer.save()  # Save the new Event to the database
                 # Notify cleaning staff
                cleaning_staff = CleaningStaff.objects.filter(pincode=notification.pincode)
                if cleaning_staff.exists():
                    # Logic to send message to cleaning staff (e.g., SMS/Email API integration)
                    print(f"Notification sent to cleaning staff: {cleaning_staff.values_list('name', flat=True)}")
                    print(f"cleaning staff PHONE: {cleaning_staff}")

                return Response(serializer.data, status=status.HTTP_201_CREATED)

            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Return errors if the data is invalid
        except DivisionalOffice.DoesNotExist:
            return Response({"error": "User is not associated with a divisional office."}, status=status.HTTP_403_FORBIDDEN)
        
       
       
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
                return Notification.objects.filter(pincode=user_pincode,level="SUBDIVISIONAL")
            
            elif hasattr(user, 'is_divisional') and user.is_divisional:
                # Fetch notifications for all post offices under the divisional office
                division_pincode = DivisionalOffice.objects.get(user=user).pincode
                post_offices = PostOffice.objects.filter(division_pincode=division_pincode)
                return Notification.objects.filter(pincode__in=post_offices, level="DIVISIONAL")
            
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
                instance.is_resolved = False
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
