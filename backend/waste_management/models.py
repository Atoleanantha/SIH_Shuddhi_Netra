from django.db import models
from post_office.models import PostOffice
from datetime import date
# Create your models here.

class CleaningStaff(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    contactNo = models.CharField(max_length=15)
    pincode = models.ForeignKey(PostOffice, on_delete=models.CASCADE)

class Event(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    attachment = models.FileField(upload_to='attachments/')
    date_time = models.DateTimeField()

class EventReport(models.Model):
    id = models.AutoField(primary_key=True)
    pincode = models.ForeignKey(PostOffice, on_delete=models.CASCADE)
    report_description = models.TextField()
    name = models.CharField(max_length=255)
    atLocation = models.BooleanField(default=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    attached_report = models.FileField(upload_to='reports/')
    date_time = models.DateTimeField()

class Ewaste(models.Model):
    id = models.AutoField(primary_key=True)
    no_of_units = models.PositiveIntegerField()
    date_time = models.DateTimeField()
    name = models.CharField(max_length=255)
    pincode = models.ForeignKey(PostOffice, on_delete=models.CASCADE)

class PaperWaste(models.Model):
    id = models.AutoField(primary_key=True)
    weight = models.FloatField()
    date = models.DateField(default=date.today)
    pincode = models.ForeignKey(PostOffice, on_delete=models.CASCADE)

class SelledPaperWaste(models.Model):
    id = models.AutoField(primary_key=True)
    total_weight = models.FloatField()
    selling_price_per_unit = models.FloatField()
    total_price = models.FloatField()
    date = models.DateField(default=date.today)
    pincode = models.ForeignKey(PostOffice, on_delete=models.CASCADE)
