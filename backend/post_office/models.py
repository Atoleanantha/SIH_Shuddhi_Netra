from django.db import models

class PostOffice(models.Model):
    pincode = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=255)
    contactNo = models.CharField(max_length=15)
    address = models.TextField()
    division_pincode = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.pincode
