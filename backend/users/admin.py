from django.contrib import admin
from .models import User, DivisionalOffice,SubDivisionalOffice

# Register your models here.

admin.site.register(User)
admin.site.register(DivisionalOffice)
admin.site.register(SubDivisionalOffice)