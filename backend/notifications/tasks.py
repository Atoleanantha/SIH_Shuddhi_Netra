
from celery import shared_task
from django.utils.timezone import now
from .models import Notification
import logging

@shared_task
def escalate_unresolved_notifications():
    """
    Task to automatically escalate unresolved notifications to divisional office.
    """
    logging.info("escalate_unresolved_notifications called")
    unresolved_notifications = Notification.objects.filter(
        is_resolved=False,
        level='SUBDIVISIONAL',
        escalation_time__lte=now()
    )
    for notification in unresolved_notifications:
        notification.escalate_to_divisional()
        logging.info(f"Notification {notification.id} escalated to divisional office.")
    return "Done"
