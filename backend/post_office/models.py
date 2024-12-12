from django.db import models 

class PostOffice(models.Model):
    pincode = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=255)
    contact_no = models.CharField(max_length=15)
    address = models.TextField()
    division_pincode = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.FloatField(default=5.0)
    def __str__(self):
        return self.pincode

    def calculate_rating(self):
        """Calculate the rating for the post office."""
        from django.apps import apps  # Lazy import to avoid circular dependency
        Notification = apps.get_model('notifications', 'Notification')
        Complaint = apps.get_model('notifications', 'Complaint')

        base_rating = 5.0  # Start with a full rating
        notifications = Notification.objects.filter(pincode=self, is_resolved=False).count()
        complaints = Complaint.objects.filter(pincode=self, action=False).count()

        # Deduct points based on unresolved notifications and complaints
        penalty_per_notification = 0.2  # Adjust weight as needed
        penalty_per_complaint = 0.3  # Adjust weight as needed

        deductions = (notifications * penalty_per_notification) + (complaints * penalty_per_complaint)
        final_rating = max(0, base_rating - deductions)  # Ensure rating doesn't go below 0

        self.rating = final_rating
        self.save()
        
        # base_rating = 10.0  # Start with a full rating
        # notificationsR = Notification.objects.filter(pincode=self, is_resolved=True).count()
        # notificationsN = Notification.objects.filter(pincode=self, is_resolved=False).count()
        # complaintsA = Complaint.objects.filter(pincode=self, action=True).count()
        # complaintsN = Complaint.objects.filter(pincode=self, action=False).count()
        
        # ratio1=(notificationsR/notificationsN)*10
        # ratio2=(complaintsA/complaintsN)*10
        
        # # Deduct points based on unresolved notifications and complaints
        # # penalty_per_notification = 0.2  # Adjust weight as needed
        # # penalty_per_complaint = 0.3  # Adjust weight as needed

        # # deductions = (notifications * penalty_per_notification) + (complaints * penalty_per_complaint)
        # # final_rating = max(0, base_rating - deductions)  # Ensure rating doesn't go below 0

        # self.rating = (ratio1+ratio2)/2
        # self.save()

        return self.rating
        