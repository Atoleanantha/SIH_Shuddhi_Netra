from rest_framework import serializers
from waste_management.models import CleaningStaff, Event,EventReport,Ewaste,PaperWaste,SelledPaperWaste

class CleaningStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = CleaningStaff
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class EventReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventReport
        fields = '__all__'

class EwasteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ewaste
        fields = '__all__'

class PaperWasteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaperWaste
        fields = '__all__'

class SelledPaperWasteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelledPaperWaste
        fields = '__all__'
