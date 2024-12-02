from rest_framework import serializers
from .models import Notification
from rest_framework import serializers
from post_office.models import PostOffice

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class NotificationWithPostOfficeSerializer(serializers.ModelSerializer):
    post_office_name = serializers.SerializerMethodField()
    post_office_address = serializers.SerializerMethodField()
    post_office_division = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = '__all__'

    def get_post_office_name(self, obj):
        try:
            return PostOffice.objects.get(pincode=obj.pincode).name
        except PostOffice.DoesNotExist:
            return None

    def get_post_office_address(self, obj):
        try:
            return PostOffice.objects.get(pincode=obj.pincode).address
        except PostOffice.DoesNotExist:
            return None

    def get_post_office_division(self, obj):
        try:
            return PostOffice.objects.get(pincode=obj.pincode).division_pincode
        except PostOffice.DoesNotExist:
            return None
