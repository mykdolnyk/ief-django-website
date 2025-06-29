from django.http import HttpRequest


def notification_count(request: HttpRequest):
    return {'notification_count': request.user.notifications.filter(is_seen=False).count()}
