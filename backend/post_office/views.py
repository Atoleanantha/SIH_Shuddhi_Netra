from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import PostOffice
from .serializers import PostOfficeSerializer
from users.models import DivisionalOffice
from users.api.permissions import IsDivisionalOffice
import logging

class PostOfficeViewSet(APIView):
    """
    A ViewSet for managing PostOffice objects.
    """
    
    permission_classes = [permissions.IsAuthenticated, IsDivisionalOffice]
    queryset = PostOffice.objects.all()
    serializer_class = PostOfficeSerializer

    @action(detail=True, methods=['put', 'patch'], permission_classes=[permissions.IsAuthenticated & IsDivisionalOffice])
    def update_post_office(self, request, *args, **kwargs):
        """
        Handle PUT/PATCH request: Update a specific PostOffice.
        Only allow updates if the PostOffice's division_pincode matches the current user's division.
        """
        try:
            # Get the PostOffice instance using the pincode (primary key)
            post_office = self.get_object()
            
            # Get the current user's division pincode from the DivisionalOffice model
            current_user_division = DivisionalOffice.objects.get(user=request.user).pincode

            # Check if the division pincode of the post office matches the user's division pincode
            if post_office.division_pincode != current_user_division:
                return Response({"error": "You are not authorized to update this post office."}, status=status.HTTP_403_FORBIDDEN)

            # If the post office belongs to the user's division, update it
            # Update the division_pincode if provided in the request
            if 'division_pincode' in request.data:
                request.data['division_pincode'] = current_user_division
            
            # Serialize the data
            serializer = PostOfficeSerializer(post_office, data=request.data, partial=True)  # partial=True allows partial updates
            
            if serializer.is_valid():  # Check if the data is valid
                serializer.save()  # Save the updated PostOffice to the database
                return Response(serializer.data, status=status.HTTP_200_OK)  # Return the updated PostOffice data with a 200 OK status
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Return errors if the data is invalid
        except DivisionalOffice.DoesNotExist:
            return Response({"error": "User is not associated with a divisional office."}, status=status.HTTP_403_FORBIDDEN)

        except PostOffice.DoesNotExist:
            return Response({"error": "PostOffice not found."}, status=status.HTTP_404_NOT_FOUND)
        

    @action(detail=True, methods=['delete'], permission_classes=[permissions.IsAuthenticated& IsDivisionalOffice])
    def delete(self, request, *args, **kwargs):
        """
        Handle DELETE request: Delete a specific PostOffice by pincode.
        Only allow deletion if the PostOffice's division_pincode matches the current user's division.
        """
        try:
            # Get the PostOffice instance using the pincode (primary key)
            post_office = self.get_object()
            
            # Get the current user's division pincode from the DivisionalOffice model
            current_user_division = DivisionalOffice.objects.get(user=request.user).pincode

            # Check if the division pincode of the post office matches the user's division pincode
            if post_office.division_pincode != current_user_division:
                return Response({"error": "You are not authorized to delete this post office."}, status=status.HTTP_403_FORBIDDEN)

            # If the post office belongs to the user's division, delete it
            post_office.delete()
            return Response({"message": "PostOffice deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        
        except DivisionalOffice.DoesNotExist:
            return Response({"error": "User is not associated with a divisional office."}, status=status.HTTP_403_FORBIDDEN)
        
        except PostOffice.DoesNotExist:
            return Response({"error": "PostOffice not found."}, status=status.HTTP_404_NOT_FOUND)


    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated& IsDivisionalOffice])
    def post(self, request, *args, **kwargs):
        """
        Handle POST request: Create a new PostOffice with the division_pincode set to the user's associated pincode.
        """
        try:
            # Get the current user's associated division pincode from DivisionalOffice
            current_user_division = DivisionalOffice.objects.get(user=request.user).pincode

            # Add the division_pincode to the request data
            request.data['division_pincode'] = current_user_division

            # Serialize the data
            serializer = PostOfficeSerializer(data=request.data)
            if serializer.is_valid():  # Check if the data is valid
                serializer.save()  # Save the new PostOffice to the database
                return Response(serializer.data, status=status.HTTP_201_CREATED)  # Return the created PostOffice data with a 201 CREATED status
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Return errors if the data is invalid
        except DivisionalOffice.DoesNotExist:
            return Response({"error": "User is not associated with a divisional office."}, status=status.HTTP_403_FORBIDDEN)
        



    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated& IsDivisionalOffice])
    def get(self, request):
        """
        Custom action to filter PostOffices by division.
        """
       
        try:
            # Get the current user's division
            current_user_division = DivisionalOffice.objects.get(user=request.user).pincode
            # print("cuurent", current_user_division)
            offices = self.queryset.filter(division_pincode=current_user_division)
            serializer = PostOfficeSerializer(offices, many=True)
            if len(serializer.data):
                return Response({"message": "User is not associated with a divisional office."}, status=403)
            return Response({"data":serializer.data,"message": "User is not associated with a divisional office."})
        except DivisionalOffice.DoesNotExist:
            return Response({"error": "User is not associated with a divisional office."}, status=403)
