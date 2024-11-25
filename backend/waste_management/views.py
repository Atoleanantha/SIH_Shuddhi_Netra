from django.shortcuts import render
from waste_management.models import Ewaste,PaperWaste,SelledPaperWaste,CleaningStaff, Event,EventReport
from waste_management.serializers import EventReportSerializer,EventSerializer, EwasteSerializer,PaperWasteSerializer,SelledPaperWasteSerializer,CleaningStaffSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from post_office.models import PostOffice
from rest_framework.permissions import IsAuthenticated
from users.api.permissions import IsDivisionalOffice,IsSubDivisionalOffice
from django.db.models import Sum
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
# Create your views here.

'''******************************* Event  Managemnt  *****************************************'''

from users.models import DivisionalOffice,SubDivisionalOffice
from users.api.serializers import DivisionalOfficeSerializer,SubDivisionalOfficeSerializer

class EventViewSet(viewsets.GenericViewSet):
    """
    Custom ViewSet for Event:
    - Create/Update: Divisional Officers only.
    - Retrieve/List: Subdivision users.
    """

    permission_classes=[IsAuthenticated]
    serializer_class=EventSerializer
    queryset=Event.objects.all()

    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated& IsDivisionalOffice])
    def create_event(self, request, *args, **kwargs):
        """
        Handle POST request: Create a new PostOffice with the division_pincode set to the user's associated pincode.
        """
        user = request.user
        try:
            # Get the current user's associated division pincode from DivisionalOffice
            current_user_division = DivisionalOffice.objects.get(user_id=user.id).pincode

            #get post office
            post_office=PostOffice.objects.get(pincode=current_user_division).pincode


            # Add the division_pincode to the request data
            request.data['pincode'] = post_office

            # Serialize the data
            serializer = EventSerializer(data=request.data)
            if serializer.is_valid():  # Check if the data is valid
                serializer.save()  # Save the new Event to the database
                return Response({"data":serializer.data,"message":current_user_division}, status=status.HTTP_201_CREATED)  # Return the created Event data with a 201 CREATED status
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Return errors if the data is invalid
        except DivisionalOffice.DoesNotExist:
            return Response({"error": "User is not associated with a divisional office."}, status=status.HTTP_403_FORBIDDEN)
        
       


    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def get_event(self, request):
        """
        Custom action to filter PostOffices by division.
        """
        
        try:
            current_user=request.user
            current_user_division=None
            if current_user.is_divisional:
                # Get the current user's division
                current_user_division = DivisionalOffice.objects.get(user=current_user).pincode
                
            elif current_user.is_sub_divisional:
                current_user_division = SubDivisionalOffice.objects.get(user=current_user).division_pincode
            
            events=self.queryset.filter(pincode=current_user_division)
            serializer = EventSerializer(events, many=True)
            if len(serializer.data) ==0:
                return Response({"message": "No events found"}, status=403)
            return Response({"data":serializer.data,"message": "Events fetched succefully!"})
        except Event.DoesNotExist:
            return Response({"error": "No events"}, status=403)
        
    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated& IsDivisionalOffice])
    def delete_event(self, request, *args, **kwargs):
        """
        Handle DELETE request: Delete a specific Event by id.
        Only allow deletion if the Event's pincode matches the current user's division.
        """
        try:
            # Get the Event instance using the id (primary key)
            current_event = self.get_object()
            
            # Get the current user's division pincode from the DivisionalOffice model
            current_user_division = DivisionalOffice.objects.get(user=request.user).pincode

            # Check if the division pincode of the event matches the user's division pincode
            if current_event.pincode != current_user_division:
                return Response({"error": "You are not authorized to delete this event."}, status=status.HTTP_403_FORBIDDEN)

            # If the event belongs to the user's division, delete it
            current_event.delete()
            return Response({"message": "Event deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        
        except Event.DoesNotExist:
            return Response({"error": "User is not associated with a divisional office."}, status=status.HTTP_403_FORBIDDEN)
    

    @action(detail=True, methods=['put', 'patch'], permission_classes=[IsAuthenticated & IsDivisionalOffice])
    def update_event(self, request, *args, **kwargs):
        """
        Handle PUT/PATCH request: Update a specific PostOffice.
        Only allow updates if the PostOffice's division_pincode matches the current user's division.
        """
        try:
            # Get the Event instance using the pincode (primary key)
            current_event = self.get_object()
            
            # Get the current user's division pincode from the DivisionalOffice model
            current_user_division = DivisionalOffice.objects.get(user=request.user).pincode

            # Check if the  pincode of the event matches the user's division pincode
            if current_event.pincode != current_user_division:
                return Response({"error": "You are not authorized to update this Event."}, status=status.HTTP_403_FORBIDDEN)

            # If the event belongs to the user's division, update it
            # Update the division_pincode if provided in the request
            if 'pincode' in request.data:
                request.data['division_pincode'] = current_user_division
            
            # Serialize the data
            serializer = EventSerializer(current_event, data=request.data, partial=True)  # partial=True allows partial updates
            
            if serializer.is_valid():  # Check if the data is valid
                serializer.save()  # Save the updated PostOffice to the database
                return Response(serializer.data, status=status.HTTP_200_OK)  # Return the updated Event data with a 200 OK status
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Return errors if the data is invalid
        except DivisionalOffice.DoesNotExist:
            return Response({"error": "User is not associated with a divisional office."}, status=status.HTTP_403_FORBIDDEN)

        except PostOffice.DoesNotExist:
            return Response({"error": "Event not found."}, status=status.HTTP_404_NOT_FOUND)
        

        



class EventReportViewSet(viewsets.GenericViewSet):
    """
    Custom ViewSet for EventReport:
    - Create: Subdivision users only.
    - Retrieve/List: Divisional Officers only.
    """

    permission_classes=[IsAuthenticated]
    serializer_class=EventReportSerializer
    queryset=EventReport.objects.all()

    '''*************** Post Report Method ***************'''


    @action(detail=False, methods=['post'],url_path="create-report", permission_classes=[IsAuthenticated& IsSubDivisionalOffice])
    def create(self, request, *args, **kwargs):
        """
        Handle POST request: Create a new EventReport and associate it with an Event.

        {
            "event_id": 1,
            "report_description": "Report for community event",
            "name": "John Doe",
            "atLocation": true,
            "attached_report": "<binary file>",
            "date_time": "2024-12-01T10:30:00Z"
        }


        """
        try:
            # Get the SubDivisionalOffice user's associated division pincode
            current_user_division = SubDivisionalOffice.objects.get(user=request.user).division_pincode

            # Extract the event ID from the request data
            event_id = request.data.get('event_id')
            if not event_id:
                return Response({"error": "Event ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the corresponding Event
            try:
                event = Event.objects.get(id=event_id)
            except Event.DoesNotExist:
                return Response({"error": "Event not found."}, status=status.HTTP_404_NOT_FOUND)

            # Check if the Event's pincode matches the user's division
            if event.pincode != current_user_division:
                return Response({"error": "You are not authorized to add a report to this event."}, status=status.HTTP_403_FORBIDDEN)

            # Add the event and pincode to the request data
            request.data['event'] = event.id
            request.data['pincode'] = current_user_division

            # Serialize and validate the data
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()  # Save the new EventReport to the database
                return Response(
                    {"data": serializer.data, "message": "Event report created successfully."}, 
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except SubDivisionalOffice.DoesNotExist:
            return Response({"error": "User is not associated with a sub-divisional office."}, status=status.HTTP_403_FORBIDDEN)



    '''*************** Get Report Method ***************'''


    @action(detail=False, methods=['get'], url_path="get-reports", permission_classes=[IsAuthenticated])
    def get(self, request, *args, **kwargs):
        """
        Handle GET request:
        - Subdivisional users get all reports in their division.
        - Divisional users get all reports for a specific event.

        + endpoint event-management/event-report/get-reports/?event_id=4

        """
        try:
            user = request.user
            if hasattr(user, 'is_sub_divisional') and user.is_sub_divisional:
                # Subdivisional users can get all reports in their division
                current_user_division = SubDivisionalOffice.objects.get(user=user).division_pincode
                reports = self.queryset.filter(pincode=current_user_division)
            elif hasattr(user, 'is_divisional') and user.is_divisional:
                # Divisional users get reports for a specific event
                event_id = request.query_params.get('event_id')
                if not event_id:
                    return Response({"error": "Event ID is required for divisional users."}, status=status.HTTP_400_BAD_REQUEST)
                
                # Fetch the event and ensure it belongs to the user's division
                current_user_division = DivisionalOffice.objects.get(user=user).pincode
                try:
                    event = Event.objects.get(id=event_id, pincode=current_user_division)
                except Event.DoesNotExist:
                    return Response({"error": "Event not found or not authorized to access it."}, status=status.HTTP_404_NOT_FOUND)

                # Get all reports for the specified event
                reports = self.queryset.filter(event=event)
            else:
                return Response({"error": "You do not have permission to view reports."}, status=status.HTTP_403_FORBIDDEN)

            # Serialize and return the reports
            serializer = self.get_serializer(reports, many=True)
            if not serializer.data:
                return Response({"message": "No reports found."}, status=status.HTTP_404_NOT_FOUND)

            return Response({"data": serializer.data, "message": "Reports fetched successfully."}, status=status.HTTP_200_OK)

        except SubDivisionalOffice.DoesNotExist:
            return Response({"error": "User is not associated with a subdivision."}, status=status.HTTP_403_FORBIDDEN)
        except DivisionalOffice.DoesNotExist:
            return Response({"error": "User is not associated with a divisional office."}, status=status.HTTP_403_FORBIDDEN)



    '''*************** Delete Report Method ***************'''

    @action(detail=True, methods=['delete'], url_path="delete-report", permission_classes=[IsAuthenticated & IsSubDivisionalOffice])
    def delete(self, request, pk=None, *args, **kwargs):
        """
        Handle DELETE request: Allow only the uploader (sub-divisional user) to delete the report.

        + endpoint event-management/event-report/<id>/delete-report/

        """
        try:
            # Get the EventReport instance using the primary key
            event_report = self.get_object()

            # Ensure the requesting user is a sub-divisional user
            if not hasattr(request.user, 'is_sub_divisional') or not request.user.is_sub_divisional:
                return Response({"error": "You do not have permission to delete this report."}, status=status.HTTP_403_FORBIDDEN)

            # Check if the current user is the uploader
            current_user_pincode = SubDivisionalOffice.objects.get(user=request.user).pincode
            if event_report.pincode != current_user_pincode:
                return Response({"error": "You can only delete reports uploaded by you."}, status=status.HTTP_403_FORBIDDEN)

            # If the user is authorized, delete the report
            event_report.delete()
            return Response({"message": "Event report deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

        except EventReport.DoesNotExist:
            return Response({"error": "Event report not found."}, status=status.HTTP_404_NOT_FOUND)
        except SubDivisionalOffice.DoesNotExist:
            return Response({"error": "User is not associated with a sub-divisional office."}, status=status.HTTP_403_FORBIDDEN)



    '''*************** Update Report Method ***************'''

    @action(detail=True, methods=['put', 'patch'], url_path="update-report", permission_classes=[IsAuthenticated & IsSubDivisionalOffice])
    def update(self, request, pk=None, *args, **kwargs):
        """
        Handle PUT/PATCH request: Allow only the uploader (sub-divisional user) to update the report
        and automatically update the date_time field to the latest timestamp.

        + endpoint event-management/event-report/<id>/update-report/

        """
        try:
            # Get the EventReport instance using the primary key
            event_report = self.get_object()

            # Ensure the requesting user is a sub-divisional user
            if not hasattr(request.user, 'is_sub_divisional') or not request.user.is_sub_divisional:
                return Response({"error": "You do not have permission to update this report."}, status=status.HTTP_403_FORBIDDEN)

            # Check if the current user is the uploader
            current_user_pincode = SubDivisionalOffice.objects.get(user=request.user).pincode
            if event_report.pincode != current_user_pincode:
                return Response({"error": "You can only update reports uploaded by you."}, status=status.HTTP_403_FORBIDDEN)

            # Update the report data
            data = request.data.copy()
            data['date_time'] = timezone.now()  # Update the date_time to the latest timestamp

            serializer = self.get_serializer(event_report, data=data, partial=True)  # Allow partial updates
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Event report updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except EventReport.DoesNotExist:
            return Response({"error": "Event report not found."}, status=status.HTTP_404_NOT_FOUND)
        except SubDivisionalOffice.DoesNotExist:
            return Response({"error": "User is not associated with a sub-divisional office."}, status=status.HTTP_403_FORBIDDEN)




'''******************************* Waste  Managemnt  *****************************************'''



'''***************** EWaste ************************'''
class EwasteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated ]

    @action(detail=False, methods=['post'], url_path='add-data', permission_classes=[IsAuthenticated])
    def post(self, request, *args, **kwargs):
        user = request.user

        # Check if the user is a sub-divisional officer
        if user.is_sub_divisional:
            sub_divisional_office = user.sub_divisional_office
            post_offices = PostOffice.objects.filter(pincode=sub_divisional_office.pincode)

            # Only allow adding e-waste data for the current post offices under the sub-division
            pincode = request.data.get('pincode')
            if pincode not in post_offices.values_list('pincode', flat=True):
                return Response({'message': 'Invalid pincode for this sub-divisional office'}, status=400)

            # Serialize and save the Ewaste data
            serializer = EwasteSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # If the user is not a sub-divisional officer, deny the request
        return Response({'message': 'Only sub-divisional officers can add data'}, status=403)
    
    @action(detail=False, methods=['get'], url_path='analytics', permission_classes=[IsAuthenticated])
    def get(self, request, *args, **kwargs):
        user = request.user

        # Check if user is a divisional officer
        if user.is_divisional:
            divisional_office = user.divisional_office
            # Get all post offices under this division
            post_offices = PostOffice.objects.filter(division_pincode=divisional_office.pincode)
            # Get all Ewaste entries for those post offices
            ewaste_data = Ewaste.objects.filter(pincode__in=post_offices)
            serializer = EwasteSerializer(ewaste_data, many=True)
            # Process the data as needed (e.g., aggregate, count, etc.)
            # Example: count total number of units
            total_units = ewaste_data.aggregate(total=Sum('no_of_units'))['total'] or 0
            return Response({'data':serializer.data,'total_units': total_units, 'message': 'Divisional office analytics'})

        # Check if user is a sub-divisional officer
        elif user.is_sub_divisional:
            sub_divisional_office = user.sub_divisional_office
            # Get the post office for the current sub-division
            post_offices = PostOffice.objects.filter(pincode=sub_divisional_office.pincode)
            print(post_offices)
            # Get Ewaste data for this sub-division's post office
            ewaste_data = Ewaste.objects.filter(pincode__in=post_offices)
            serializer = EwasteSerializer(ewaste_data, many=True)
            # Process the data as needed
            total_units = ewaste_data.aggregate(total=Sum('no_of_units'))['total'] or 0
            return Response({'data':serializer.data ,'total_units': total_units, 'message': 'Sub-divisional office analytics'})

        # If the user does not have a valid role
        return Response({'message': 'User does not have access to this data'}, status=403)
    

    @action(detail=True, methods=['delete'], url_path='delete-data', permission_classes=[IsAuthenticated])
    def delete_data(self, request, *args, **kwargs):
        user = request.user
        ewaste_entry = self.get_object()  # Fetch the specific Ewaste entry to be deleted

        # Check if the user is a sub-divisional officer
        if user.is_sub_divisional:
            sub_divisional_office = user.sub_divisional_office
            post_offices = PostOffice.objects.filter(pincode=sub_divisional_office.pincode)

            # Only allow deleting e-waste data for the current post offices under the sub-division
            if ewaste_entry.pincode not in post_offices.values_list('pincode', flat=True):
                return Response({'message': 'Invalid pincode for this sub-divisional office'}, status=400)

            # If the user is authorized, delete the Ewaste entry
            ewaste_entry.delete()
            return Response({'message': 'E-waste data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

        # Check if the user is a divisional officer (optional, can add more restrictions if necessary)
        elif user.is_divisional:
            divisional_office = user.divisional_office
            post_offices = PostOffice.objects.filter(division_pincode=divisional_office.pincode)

            # Only allow deleting e-waste data for post offices under the divisional office
            if ewaste_entry.pincode not in post_offices.values_list('pincode', flat=True):
                return Response({'message': 'Invalid pincode for this divisional office'}, status=400)

            # If the user is authorized, delete the Ewaste entry
            ewaste_entry.delete()
            return Response({'message': 'E-waste data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

        # If the user does not have the required permissions
        return Response({'message': 'User does not have access to delete this data'}, status=403)
    
    

'''***************** PaperWaste ************************'''
class PaperWasteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PaperWasteSerializer
    queryset = PaperWaste.objects.all()

    @action(detail=False, methods=['post'], url_path='add-data', permission_classes=[IsAuthenticated])
    def post(self, request, *args, **kwargs):
        user = request.user

        # Check if the user is a sub-divisional officer
        if user.is_sub_divisional:
            sub_divisional_office = user.sub_divisional_office
            post_offices = PostOffice.objects.filter(pincode=sub_divisional_office.pincode)

            # Only allow adding paper waste data for the current post offices under the sub-division
            pincode = request.data.get('pincode')
            if pincode not in post_offices.values_list('pincode', flat=True):
                return Response({'message': 'Invalid pincode for this sub-divisional office'}, status=400)

            # Serialize and save the PaperWaste data
            serializer = PaperWasteSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # If the user is not a sub-divisional officer, deny the request
        return Response({'message': 'Only sub-divisional officers can add data'}, status=403)

    @action(detail=False, methods=['get'], url_path='analytics', permission_classes=[IsAuthenticated])
    def get(self, request, *args, **kwargs):
        user = request.user

        # Check if user is a divisional officer
        if user.is_divisional:
            divisional_office = user.divisional_office
            # Get all post offices under this division
            post_offices = PostOffice.objects.filter(division_pincode=divisional_office.pincode)
            # Get all PaperWaste entries for those post offices
            paper_waste_data = PaperWaste.objects.filter(pincode__in=post_offices)
            # Process the data as needed (e.g., aggregate, count, etc.)
            total_weight = paper_waste_data.aggregate(total=Sum('weight'))['total'] or 0

            serializer=PaperWasteSerializer(paper_waste_data, many=True)
            return Response({'data': serializer.data, 'total_weight': total_weight, 'message': 'Divisional office analytics'})

        # Check if user is a sub-divisional officer
        elif user.is_sub_divisional:
            sub_divisional_office = user.sub_divisional_office
            # Get the post office for the current sub-division
            post_offices = PostOffice.objects.filter(pincode=sub_divisional_office.pincode)
            # Get PaperWaste data for this sub-division's post office
            paper_waste_data = PaperWaste.objects.filter(pincode__in=post_offices)
            # Process the data as needed
            total_weight = paper_waste_data.aggregate(total=Sum('weight'))['total'] or 0

            serializer=PaperWasteSerializer(paper_waste_data, many=True)

            return Response({'data': serializer.data, 'total_weight': total_weight, 'message': 'Sub-divisional office analytics'})

        # If the user does not have a valid role
        return Response({'message': 'User does not have access to this data'}, status=403)

    @action(detail=True, methods=['delete'], url_path='delete-data', permission_classes=[IsAuthenticated])
    def delete_data(self, request, *args, **kwargs):
        user = request.user
        paper_waste_entry = self.get_object()  # Fetch the specific PaperWaste entry to be deleted

        # Check if the user is a sub-divisional officer
        if user.is_sub_divisional:
            sub_divisional_office = user.sub_divisional_office
            post_offices = PostOffice.objects.filter(pincode=sub_divisional_office.pincode)

            # Only allow deleting paper waste data for the current post offices under the sub-division
            if paper_waste_entry.pincode not in post_offices.values_list('pincode', flat=True):
                return Response({'message': 'Invalid pincode for this sub-divisional office'}, status=400)

            # If the user is authorized, delete the PaperWaste entry
            paper_waste_entry.delete()
            return Response({'message': 'Paper waste data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

        # Check if the user is a divisional officer (optional, can add more restrictions if necessary)
        elif user.is_divisional:
            divisional_office = user.divisional_office
            post_offices = PostOffice.objects.filter(division_pincode=divisional_office.pincode)

            # Only allow deleting paper waste data for post offices under the divisional office
            if paper_waste_entry.pincode not in post_offices.values_list('pincode', flat=True):
                return Response({'message': 'Invalid pincode for this divisional office'}, status=400)

            # If the user is authorized, delete the PaperWaste entry
            paper_waste_entry.delete()
            return Response({'message': 'Paper waste data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

        # If the user does not have the required permissions
        return Response({'message': 'User does not have access to delete this data'}, status=403)
    



'''***************** SelledPaperWasteViewSet ************************'''
class SelledPaperWasteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SelledPaperWasteSerializer
    queryset = SelledPaperWaste.objects.all()

    @action(detail=False, methods=['post'], url_path='add-data', permission_classes=[IsAuthenticated])
    def post(self, request, *args, **kwargs):
        user = request.user

        # Check if the user is a sub-divisional officer
        if user.is_sub_divisional:
            sub_divisional_office = user.sub_divisional_office
            post_offices = PostOffice.objects.filter(pincode=sub_divisional_office.pincode)

            # Only allow adding selled paper waste data for the current post offices under the sub-division
            pincode = request.data.get('pincode')
            if pincode not in post_offices.values_list('pincode', flat=True):
                return Response({'message': 'Invalid pincode for this sub-divisional office'}, status=400)

            # Serialize and save the SelledPaperWaste data
            serializer = SelledPaperWasteSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # If the user is not a sub-divisional officer, deny the request
        return Response({'message': 'Only sub-divisional officers can add data'}, status=403)



    @action(detail=False, methods=['get'], url_path='analytics', permission_classes=[IsAuthenticated])
    def get(self, request, *args, **kwargs):
        user = request.user

        # Check if user is a divisional officer
        if user.is_divisional:
            divisional_office = user.divisional_office
            # Get all post offices under this division
            post_offices = PostOffice.objects.filter(division_pincode=divisional_office.pincode)
            # Get all SelledPaperWaste entries for those post offices
            print(post_offices)
            selled_paper_waste_data = SelledPaperWaste.objects.filter(pincode__in=post_offices)
            serializer=SelledPaperWasteSerializer(selled_paper_waste_data, many=True)
            # Process the data as needed (e.g., aggregate, count, etc.)
            total_weight = selled_paper_waste_data.aggregate(total=Sum('total_weight'))['total'] or 0
            total_price = selled_paper_waste_data.aggregate(total=Sum('total_price'))['total'] or 0
            return Response({'data': serializer.data, 'total_price':total_price,'total_weight': total_weight, 'message': 'Divisional office analytics'})

        # Check if user is a sub-divisional officer
        elif user.is_sub_divisional:
            sub_divisional_office = user.sub_divisional_office
            # Get the post office for the current sub-division
            post_offices = PostOffice.objects.filter(pincode=sub_divisional_office.pincode)
            print(post_offices)
            # Get SelledPaperWaste data for this sub-division's post office
            selled_paper_waste_data = SelledPaperWaste.objects.filter(pincode__in=post_offices)
            serializer=SelledPaperWasteSerializer(selled_paper_waste_data, many=True)
            # Process the data as needed
            total_weight = selled_paper_waste_data.aggregate(total=Sum('total_weight'))['total'] or 0
            total_price = selled_paper_waste_data.aggregate(total=Sum('total_price'))['total'] or 0
            return Response({'data': serializer.data, 'total_price':total_price,'total_weight': total_weight, 'message': 'Sub-divisional office analytics'})

        # If the user does not have a valid role
        return Response({'message': 'User does not have access to this data'}, status=403)

    @action(detail=True, methods=['delete'], url_path='delete-data', permission_classes=[IsAuthenticated])
    def delete_data(self, request, *args, **kwargs):
        user = request.user
        selled_paper_waste_entry = self.get_object()  # Fetch the specific


'''***************** CleaningStaffViewSet ************************'''

class CleaningStaffViewSet(viewsets.ModelViewSet):
    queryset = CleaningStaff.objects.all()
    serializer_class = CleaningStaffSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Ensure that only sub-divisional officers can create cleaning staff
        if not self.request.user.is_sub_divisional:
            raise PermissionDenied("Only sub-divisional officers can add cleaning staff.")
        
        # Proceed with the creation if the user is a sub-divisional officer
        user=serializer.save()
        return Response({"user":user,"message":"Succesfully Deleted!"},status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        # Ensure that only sub-divisional officers can delete cleaning staff
        if not self.request.user.is_sub_divisional:
            raise PermissionDenied("Only sub-divisional officers can delete cleaning staff.")
        
        # Proceed with deletion if the user is a sub-divisional officer
        instance.delete()
        return Response({"message:":"Succesfully Deleted!"},status=status.HTTP_202_ACCEPTED)

    # You can optionally allow all users to perform the read operations (list and retrieve)
    def get_queryset(self):
        # You can customize this to filter based on the sub-divisional office if needed
        return CleaningStaff.objects.all()
