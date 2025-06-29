from django.http import HttpRequest


def notification_count(request: HttpRequest):
    if request.user.is_authenticated:
        notifications = request.user.notifications.filter(is_seen=False).count()
    else:
        notifications = None
    return {'notification_count': notifications}
