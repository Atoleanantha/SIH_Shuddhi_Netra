# from django.db import models
# from django.contrib.auth.models import AbstractUser
# from django.db.models.signals import post_save
# from django.conf import settings
# from django.dispatch import receiver
# from rest_framework.authtoken.models import Token
# # Create your models here.

# class User(AbstractUser):
#     is_divisional=models.BooleanField(default=False)
#     is_sub_divisional=models.BooleanField(default=False)

#     def __str__(self):
#         return self.username
    

# @receiver(post_save,sender=settings.AUTH_USER_MODEL)
# def create_auth_token(sender,instance=None, created=False,**kwargs):
#     if created:
#         Token.objects.create(user=instance)

# class DivisionalOffice(models.Model):
#     user=models.OneToOneField(User,related_name="Divisional_office",on_delete=models.CASCADE)
#     full_name=models.CharField(max_length=50)
#     phone_number=models.CharField(max_length=10)
#     email=models.EmailField()
#     address=models.TextField()
#     pincode=models.IntegerField()
#     def  __str__(self):
#         return self.user.username
    

# class SubDivisionalOffice(models.Model):
#     user=models.OneToOneField(User,related_name="Sub_Divisional_office",on_delete=models.CASCADE)
#     full_name=models.CharField(max_length=50)
#     phone_number=models.CharField(max_length=10)
#     email=models.EmailField()
#     address=models.TextField()
#     pincode=models.IntegerField()
#     division_pincode=models.IntegerField()
#     def  __str__(self):
#         return self.user.username

    
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.conf import settings
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


# Custom User model
class User(AbstractUser):
    is_divisional = models.BooleanField(default=False)
    is_sub_divisional = models.BooleanField(default=False)

    def __str__(self):
        return self.username


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


# Divisional Office model
class DivisionalOffice(models.Model):
    user = models.OneToOneField(User, related_name="divisional_office", on_delete=models.CASCADE)
    full_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=10)
    email = models.EmailField()
    address = models.TextField()
    pincode = models.IntegerField()

    def __str__(self):
        return self.full_name


# Sub Divisional Office model
class SubDivisionalOffice(models.Model):
    user = models.OneToOneField(User, related_name="sub_divisional_office", on_delete=models.CASCADE)
    full_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=10)
    email = models.EmailField()
    address = models.TextField()
    pincode = models.IntegerField()
    division_pincode = models.IntegerField()

    def __str__(self):
        return self.full_name
