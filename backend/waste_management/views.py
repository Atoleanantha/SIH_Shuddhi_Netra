from django.shortcuts import render
from waste_management.models import Ewaste,PaperWaste,SelledPaperWaste,CleaningStaff
from waste_management.serializers import EwasteSerializer,PaperWasteSerializer,SelledPaperWasteSerializer,CleaningStaffSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from post_office.models import PostOffice
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
# Create your views here.

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
