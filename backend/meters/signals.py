import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Alert, Notification
from .sms_service import send_sms

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Alert)
def send_alert_sms_on_create(sender, instance, created, **kwargs):
    if not created:
        return

    user = getattr(getattr(instance, 'meter', None), 'user', None)
    phone_number = getattr(user, 'phone_number', '') if user else ''

    if not phone_number:
        Notification.objects.create(
            user=user,
            alert=instance,
            channel='sms',
            status='failed',
            recipient='',
            message=instance.message,
            error_message='User phone number not configured',
        )
        logger.warning(f"Alert {instance.id} SMS skipped: no phone number configured")
        return

    result = send_sms(phone_number, instance.message)
    success = bool(result.get('success'))

    Notification.objects.create(
        user=user,
        alert=instance,
        channel='sms',
        status='sent' if success else 'failed',
        recipient=phone_number,
        message=instance.message,
        external_id=result.get('sid') or result.get('message_id', ''),
        error_message='' if success else result.get('message', 'SMS failed'),
        sent_at=timezone.now() if success else None,
    )

    if success:
        logger.info(f"Alert SMS sent for alert {instance.id} to {phone_number}")
    else:
        logger.warning(f"Alert SMS failed for alert {instance.id}: {result.get('message')}")
