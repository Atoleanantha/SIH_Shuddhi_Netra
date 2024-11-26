from django.db import models
from post_office.models import PostOffice
from datetime import datetime, timedelta
from django.utils.timezone import now
class Notification(models.Model):
    LEVEL_CHOICES = (
        ('SUBDIVISIONAL', 'Subdivisional'),
        ('DIVISIONAL', 'Divisional'),
    )

    id = models.AutoField(primary_key=True)
    image = models.FileField()
    message = models.CharField(max_length=255)
    action_performed = models.CharField(max_length=255, blank=True, null=True)
    response = models.CharField(max_length=255, blank=True, null=True)
    is_resolved = models.BooleanField(default=False)
    createdAt = models.DateTimeField(default=now)
    updatedAt = models.DateTimeField(default=now)
    escalation_time = models.DateTimeField(default=now() + timedelta(minutes=1))
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='SUBDIVISIONAL')
    pincode = models.ForeignKey(PostOffice, on_delete=models.CASCADE)
    read=models.BooleanField(default=False)

    def escalate_to_divisional(self):
        """Escalates the notification to the divisional office."""
        self.level = 'DIVISIONAL'
        self.updatedAt = now()
        self.save()
