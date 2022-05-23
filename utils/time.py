from django.utils import timezone


def get_now():
    return timezone.now()


def get_today():
    return get_now().date()
