from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import PostOffice
from .serializers import PostOfficeSerializer
from users.models import DivisionalOffice
from users.api.permissions import IsDivisionalOffice

class PostOfficeViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for managing PostOffice objects.
    """
    queryset = PostOffice.objects.all()
    serializer_class = PostOfficeSerializer
    permission_classes = [permissions.IsAuthenticated, IsDivisionalOffice]

    def perform_create(self, serializer):
        # Custom logic when creating a new PostOffice
        serializer.save()

    def perform_destroy(self, instance):
        # Custom logic when deleting a PostOffice
        instance.delete()

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated, IsDivisionalOffice])
    def by_division(self, request):
        """
        Custom action to filter PostOffices by division.
        """
        try:
            # Get the current user's division
            current_user_division = DivisionalOffice.objects.get(user=request.user).division_id
            offices = self.queryset.filter(division_pincode=current_user_division)
            serializer = self.get_serializer(offices, many=True)
            return Response(serializer.data)
        except DivisionalOffice.DoesNotExist:
            return Response({"error": "User is not associated with a divisional office."}, status=403)
