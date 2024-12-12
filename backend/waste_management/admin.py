from django.contrib import admin
from .models import CleaningStaff,Event,EventReport,Ewaste,PaperWaste,SelledPaperWaste
# Register your models here.

admin.site.register(CleaningStaff)
admin.site.register(Event)
admin.site.register(EventReport)
admin.site.register(Ewaste)
admin.site.register(PaperWaste)
admin.site.register(SelledPaperWaste)
