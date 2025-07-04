from django.contrib.auth.signals import user_logged_in, user_login_failed, user_logged_out
from django.dispatch import receiver
from django.utils.timezone import now
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    logger.info(f"LOGIN: {user.username} at {now()} from {get_client_ip(request)}")

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    logger.warning(f"FAILED LOGIN: {credentials.get('username')} at {now()} from {get_client_ip(request)}")

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    logger.info(f"LOGOUT: {user.username} at {now()} from {get_client_ip(request)}")

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
