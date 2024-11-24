from rest_framework import serializers
from .models import PostOffice

class PostOfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model=PostOffice
        fields="__all__"
    
        